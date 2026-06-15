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


def wrap_solution(ext, qid, title, url, code):
    """Make the LeetCode snippet runnable standalone.

    The region between LC-START / LC-END markers is what submit.py sends back
    to LeetCode, so keep your solution inside it.
    """
    tag = f"{qid}. {title}  ({url})"
    cm = "#" if ext == "py" else "//"
    note = f"{cm} write your solution between the markers below (submit.py sends this)"
    start, end = f"{cm} LC-START", f"{cm} LC-END"
    if ext == "go":
        return (
            f"package main\n\n"
            f'import "fmt"\n\n'
            f"// {tag}\n"
            f"{note}\n"
            f"{start}\n"
            f"{code}\n"
            f"{end}\n\n"
            f"func main() {{\n"
            f"\t// TODO: call the solution and print results\n"
            f'\tfmt.Println("{qid}. {title}")\n'
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
            sol.write_text(wrap_solution(ext, qid, title, url, snip["code"]))

    tc = q.get("exampleTestcases")
    if tc:
        (out / "testcases.txt").write_text(tc + "\n")

    print(f"Created {out}/")
    for f in sorted(out.iterdir()):
        print(f"  {f.name}")


if __name__ == "__main__":
    main()
