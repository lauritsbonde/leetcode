#!/usr/bin/env python3
"""Fetch a LeetCode problem and scaffold a directory for it.

Usage:
    python3 fetch.py two-sum
    python3 fetch.py https://leetcode.com/problems/two-sum/
    python3 fetch.py 1            # by problem id (frontend number)
"""

import json
import re
import sys
import urllib.request
from html import unescape
from pathlib import Path

GRAPHQL = "https://leetcode.com/graphql"
HERE = Path(__file__).resolve().parent

DIFF_EMOJI = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}

LANG_EXT = {
    "python3": "py",
    "python": "py",
    "cpp": "cpp",
    "java": "java",
    "javascript": "js",
    "typescript": "ts",
    "golang": "go",
    "go": "go",
    "rust": "rs",
}

# normalize friendly aliases -> leetcode langSlug
LANG_ALIAS = {"go": "golang", "py": "python3", "python": "python3"}


def post(query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        GRAPHQL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://leetcode.com",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]


def slug_from_arg(arg):
    """Resolve a slug from a url, slug, or numeric id."""
    arg = arg.strip()
    m = re.search(r"problems/([a-z0-9-]+)", arg)
    if m:
        return m.group(1)
    if arg.isdigit():
        return slug_from_id(int(arg))
    return arg  # assume already a slug


def slug_from_id(qid):
    q = """
    query problemsetQuestionList($limit: Int, $skip: Int) {
      problemsetQuestionList: questionList(
        categorySlug: "" limit: $limit skip: $skip filters: {}
      ) { questions { frontendQuestionId titleSlug } }
    }"""
    # paginate until we find it (ids are not contiguous)
    skip = 0
    while True:
        data = post(q, {"limit": 1000, "skip": skip})
        qs = data["problemsetQuestionList"]["questions"]
        if not qs:
            break
        for item in qs:
            if int(item["frontendQuestionId"]) == qid:
                return item["titleSlug"]
        skip += 1000
    sys.exit(f"No problem with id {qid}")


def fetch(slug):
    q = """
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionFrontendId
        title
        titleSlug
        difficulty
        content
        topicTags { name }
        codeSnippets { lang langSlug code }
        exampleTestcases
        metaData
      }
    }"""
    data = post(q, {"titleSlug": slug})
    q = data["question"]
    if not q:
        sys.exit(f"Problem '{slug}' not found")
    return q


def html_to_md(html):
    """Crude HTML -> markdown. Good enough for problem descriptions."""
    s = html
    s = re.sub(r"<sup>(.*?)</sup>", r"^\1", s, flags=re.S)
    s = re.sub(r"<sub>(.*?)</sub>", r"_\1", s, flags=re.S)
    s = re.sub(r"</?(strong|b)\b[^>]*>", "**", s)
    s = re.sub(r"</?(em|i)\b[^>]*>", "*", s)
    s = re.sub(r"</?code\b[^>]*>", "`", s)
    s = re.sub(
        r"<pre\b[^>]*>(.*?)</pre>",
        lambda m: "```\n" + m.group(1).strip() + "\n```",
        s,
        flags=re.S,
    )
    s = re.sub(r"<li\b[^>]*>\s*(.*?)\s*</li>", r"- \1", s, flags=re.S)
    s = re.sub(r"</?(ul|ol)\b[^>]*>", "", s)
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"</p>", "\n\n", s)
    s = re.sub(r"<[^>]+>", "", s)  # strip remaining tags
    s = unescape(s)
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n[ \t]+", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


# --- Go test-harness generation ---------------------------------------------
#
# Turn LeetCode's metaData + exampleTestcases + the "Output:" lines in the
# description into a runnable main() that calls the solution on each example
# and prints PASS/FAIL against the expected answer.

LC_TO_GO = {
    "integer": "int",
    "long": "int64",
    "double": "float64",
    "float": "float64",
    "string": "string",
    "boolean": "bool",
    "character": "byte",
}


def go_type_of(lc_type):
    """Map a LeetCode type ('integer', 'integer[]', 'string[][]') to a Go type.

    Returns None for types we can't auto-wire (ListNode, TreeNode, ...).
    """
    t = lc_type.strip()
    depth = 0
    while t.endswith("[]"):
        depth += 1
        t = t[:-2]
    base = LC_TO_GO.get(t)
    if base is None:
        return None
    return "[]" * depth + base


def go_lit(go_type, value):
    """Render a JSON-decoded example value as a Go literal of the given type."""
    if go_type.startswith("[]"):
        elem = go_type[2:]
        items = ", ".join(go_lit(elem, v) for v in value)
        return f"{go_type}{{{items}}}"
    if go_type == "string":
        return json.dumps(value)
    if go_type == "byte":  # LC gives a 1-char string for `character`
        return "'" + value.replace("'", "\\'") + "'"
    if go_type == "bool":
        return "true" if value else "false"
    return str(value)  # int / float


def parse_expected(content):
    """Pull the example outputs, in order, out of the problem HTML."""
    outs = re.findall(r"Output:?\s*</(?:strong|b|em)>\s*([^<\n]+)", content)
    if not outs:
        outs = re.findall(r"Output:?\s*\**\s*([^<\n]+)", content)
    parsed = []
    for o in outs:
        o = unescape(o).strip().rstrip(".").strip()
        try:
            parsed.append(json.loads(o))
        except (json.JSONDecodeError, ValueError):
            return None  # bail rather than guess
    return parsed


def build_go_main(meta_json, example_testcases, content):
    """Build a Go main() with a table of example cases, or None if we can't.

    None means: fall back to the TODO stub (unsupported types / parse miss).
    """
    try:
        meta = json.loads(meta_json) if meta_json else {}
    except (json.JSONDecodeError, TypeError):
        return None

    fn = meta.get("name")
    params = meta.get("params") or []
    ret = (meta.get("return") or {}).get("type")
    if not fn or not ret:
        return None

    pgo = [go_type_of(p["type"]) for p in params]
    rgo = go_type_of(ret)
    if rgo is None or any(t is None for t in pgo):
        return None

    lines = [ln for ln in (example_testcases or "").splitlines() if ln.strip()]
    n = len(params)
    if n == 0 or len(lines) % n != 0:
        return None
    raw_cases = [lines[i:i + n] for i in range(0, len(lines), n)]

    inputs = []
    for case in raw_cases:
        try:
            inputs.append([json.loads(v) for v in case])
        except (json.JSONDecodeError, ValueError):
            return None

    expected = parse_expected(content)
    if expected is not None and len(expected) != len(inputs):
        expected = None  # counts disagree -> don't wire wants

    fields = [(p["name"], t) for p, t in zip(params, pgo)]
    width = max([len(name) for name, _ in fields] + [4])  # 'want' is 4

    decl = [f"\tcases := []struct {{"]
    for name, t in fields:
        decl.append(f"\t\t{name.ljust(width)} {t}")
    if expected is not None:
        decl.append(f"\t\t{'want'.ljust(width)} {rgo}")
    decl.append("\t}{")
    for i, args in enumerate(inputs):
        cells = [go_lit(t, v) for (_, t), v in zip(fields, args)]
        if expected is not None:
            cells.append(go_lit(rgo, expected[i]))
        decl.append("\t\t{" + ", ".join(cells) + "},")
    decl.append("\t}")

    call_args = ", ".join(f"c.{name}" for name, _ in fields)
    body = ["\n".join(decl), ""]
    if expected is None:
        body += [
            "\tfor i, c := range cases {",
            f"\t\tfmt.Printf(\"case %d: %v\\n\", i+1, {fn}({call_args}))",
            "\t}",
        ]
    else:
        cmp = (
            "reflect.DeepEqual(got, c.want)"
            if rgo.startswith("[]")
            else "got == c.want"
        )
        body += [
            "\tfor i, c := range cases {",
            f"\t\tgot := {fn}({call_args})",
            "\t\tmark := \"PASS\"",
            f"\t\tif !({cmp}) {{",
            "\t\t\tmark = \"FAIL\"",
            "\t\t}",
            "\t\tfmt.Printf(\"case %d: %s  got=%v want=%v\\n\", i+1, mark, got, c.want)",
            "\t}",
        ]
    needs_reflect = expected is not None and rgo.startswith("[]")
    return "\n".join(body), needs_reflect


def wrap_solution(ext, qid, title, url, code, go_main=None):
    """Make the LeetCode snippet runnable standalone.

    The region between LC-START / LC-END markers is what submit.py sends back
    to LeetCode, so keep your solution inside it.
    """
    tag = f"{qid}. {title}  ({url})"
    cm = "#" if ext == "py" else "//"
    note = f"{cm} write your solution between the markers below (submit.py sends this)"
    start, end = f"{cm} LC-START", f"{cm} LC-END"
    if ext == "go":
        if go_main is not None:
            main_body, needs_reflect = go_main
        else:
            main_body, needs_reflect = (
                "\t// TODO: call the solution and print results\n"
                f'\tfmt.Println("{qid}. {title}")',
                False,
            )
        imports = '"fmt"' if not needs_reflect else '(\n\t"fmt"\n\t"reflect"\n)'
        return (
            f"package main\n\n"
            f"import {imports}\n\n"
            f"// {tag}\n"
            f"{note}\n"
            f"{start}\n"
            f"{code}\n"
            f"{end}\n\n"
            f"func main() {{\n"
            f"{main_body}\n"
            f"}}\n"
        )
    return f"{cm} {tag}\n\n{note}\n{start}\n{code}\n{end}\n"


def pick_snippet(snippets, lang="python3"):
    for s in snippets:
        if s["langSlug"] == lang:
            return s
    return snippets[0] if snippets else None


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    lang = sys.argv[2] if len(sys.argv) > 2 else "golang"
    lang = LANG_ALIAS.get(lang, lang)

    slug = slug_from_arg(sys.argv[1])
    print(f"Fetching {slug} ...")
    q = fetch(slug)

    qid = q["questionFrontendId"]
    title = q["title"]
    diff = q["difficulty"]
    dirname = f"{int(qid):04d}-{q['titleSlug']}"
    out = HERE / dirname
    out.mkdir(exist_ok=True)

    tags = ", ".join(t["name"] for t in q["topicTags"]) or "—"
    body = html_to_md(q["content"])
    url = f"https://leetcode.com/problems/{q['titleSlug']}/"

    readme = f"""# {qid}. {title}

{DIFF_EMOJI.get(diff, "")} **{diff}** &nbsp; | &nbsp; [LeetCode]({url})

**Topics:** {tags}

---

{body}
"""
    (out / "README.md").write_text(readme)

    snip = pick_snippet(q["codeSnippets"], lang)
    if snip:
        ext = LANG_EXT.get(snip["langSlug"], "txt")
        sol = out / f"solution.{ext}"
        if not sol.exists():
            go_main = None
            if ext == "go":
                go_main = build_go_main(
                    q.get("metaData"), q.get("exampleTestcases"), q["content"]
                )
            sol.write_text(
                wrap_solution(ext, qid, title, url, snip["code"], go_main)
            )

    tc = q.get("exampleTestcases")
    if tc:
        (out / "testcases.txt").write_text(tc + "\n")

    print(f"Created {out}/")
    for f in sorted(out.iterdir()):
        print(f"  {f.name}")


if __name__ == "__main__":
    main()
