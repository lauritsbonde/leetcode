#!/usr/bin/env python3
"""Generate a progress section in README.md from the solved problem dirs.

Scans every `NNNN-slug/` directory, parses its README.md for difficulty and
topics, detects which languages have a solution file, and renders a summary
(counts by difficulty + a table of every problem) into README.md between the
`<!-- STATS:START -->` and `<!-- STATS:END -->` markers.

Stdlib only. Run with `make stats` or directly: `python3 stats.py`.
Pass `--page PATH` to write a standalone Jekyll page instead of touching
README (CI uses this to publish to the gh-pages branch).
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROBLEMS = os.path.join(ROOT, "problems")
README = os.path.join(ROOT, "README.md")
START = "<!-- STATS:START -->"
END = "<!-- STATS:END -->"

DIR_RE = re.compile(r"^(\d{4})-(.+)$")
# Line 3 of a problem README looks like: "🟢 **Easy** &nbsp; | &nbsp; [LeetCode](url)"
DIFF_RE = re.compile(r"\*\*(Easy|Medium|Hard)\*\*")
TOPICS_RE = re.compile(r"^\*\*Topics:\*\*\s*(.+)$", re.M)
LINK_RE = re.compile(r"\[LeetCode\]\((https?://[^\)]+)\)")

DIFF_EMOJI = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}
EXT_LANG = {
    ".go": "Go", ".py": "Python", ".cpp": "C++", ".java": "Java",
    ".js": "JS", ".ts": "TS", ".rs": "Rust",
}
# LeetCode langSlug (as stored in .solved.json) -> display name.
SLUG_LANG = {
    "golang": "Go", "python3": "Python", "cpp": "C++", "java": "Java",
    "javascript": "JS", "typescript": "TS", "rust": "Rust",
}


def parse_problem(dirname):
    m = DIR_RE.match(dirname)
    if not m:
        return None
    pid, slug = int(m.group(1)), m.group(2)
    path = os.path.join(PROBLEMS, dirname)
    readme = os.path.join(path, "README.md")

    title = slug.replace("-", " ").title()
    difficulty = "?"
    topics = ""
    link = f"https://leetcode.com/problems/{slug}/"
    if os.path.isfile(readme):
        with open(readme, encoding="utf-8") as f:
            text = f.read()
        first = text.splitlines()[0] if text else ""
        if first.startswith("# "):
            title = first[2:].strip()
        dm = DIFF_RE.search(text)
        if dm:
            difficulty = dm.group(1)
        tm = TOPICS_RE.search(text)
        if tm:
            topics = tm.group(1).strip()
        lm = LINK_RE.search(text)
        if lm:
            link = lm.group(1)

    # 'Solved' = an Accepted judge verdict recorded by submit.py, not merely a
    # scaffolded dir. .solved.json lists every language that got Accepted.
    solved_langs, fastest = [], None
    rec_path = os.path.join(path, ".solved.json")
    if os.path.isfile(rec_path):
        try:
            with open(rec_path, encoding="utf-8") as f:
                rec = json.load(f)
            for slangslug, info in (rec.get("solutions") or {}).items():
                solved_langs.append(SLUG_LANG.get(slangslug, slangslug))
                rt = (info or {}).get("runtime")
                if rt and fastest is None:
                    fastest = rt
        except (ValueError, OSError):
            pass

    return {
        "id": pid, "slug": slug, "title": title, "difficulty": difficulty,
        "topics": topics, "link": link,
        "solved": bool(solved_langs),
        "langs": sorted(set(solved_langs)),
        "runtime": fastest,
    }


def render(problems):
    solved = [p for p in problems if p["solved"]]
    unsolved = len(problems) - len(solved)
    counts = {"Easy": 0, "Medium": 0, "Hard": 0}
    for p in solved:
        if p["difficulty"] in counts:
            counts[p["difficulty"]] += 1

    lines = []
    lines.append(f"**Solved: {len(solved)}** &nbsp; | &nbsp; "
                 f"🟢 Easy {counts['Easy']} &nbsp; · &nbsp; "
                 f"🟡 Medium {counts['Medium']} &nbsp; · &nbsp; "
                 f"🔴 Hard {counts['Hard']}")
    lines.append("")
    lines.append("| # | Problem | Difficulty | Languages | Runtime | Topics |")
    lines.append("|---|---------|------------|-----------|---------|--------|")
    for p in sorted(solved, key=lambda x: x["id"]):
        emoji = DIFF_EMOJI.get(p["difficulty"], "")
        langs = ", ".join(p["langs"]) or "—"
        diff = f"{emoji} {p['difficulty']}".strip()
        lines.append(
            f"| {p['id']} | [{p['title']}]({p['link']}) | {diff} | "
            f"{langs} | {p['runtime'] or '—'} | {p['topics']} |"
        )
    if unsolved:
        lines.append("")
        lines.append(f"_{unsolved} more scaffolded but not yet Accepted._")
    return "\n".join(lines)


def render_block(problems):
    """The README marker block (used by local `make stats`)."""
    return f"{START}\n\n{render(problems)}\n\n{END}"


def build_page(problems):
    """A standalone Jekyll page for GitHub Pages."""
    return (
        "---\n"
        "title: LeetCode Progress\n"
        "---\n\n"
        "# LeetCode Progress\n\n"
        f"{render(problems)}\n\n"
        "_Generated from the repo by CI on every push to main._\n"
    )


def main():
    problems = [
        p for d in os.listdir(PROBLEMS)
        if os.path.isdir(os.path.join(PROBLEMS, d))
        for p in [parse_problem(d)]
        if p
    ]

    # --page PATH: write a standalone page (used by CI to publish to gh-pages).
    if "--page" in sys.argv:
        path = sys.argv[sys.argv.index("--page") + 1]
        with open(path, "w", encoding="utf-8") as f:
            f.write(build_page(problems))
        print(f"Wrote {path} ({len(problems)} problems).")
        return 0

    # Default: inject the table into README between markers (local convenience).
    block = render_block(problems)
    with open(README, encoding="utf-8") as f:
        content = f.read()
    if START in content and END in content:
        new = re.sub(
            re.escape(START) + r".*?" + re.escape(END),
            lambda _: block, content, flags=re.S,
        )
    else:
        new = content.rstrip() + "\n\n## Progress\n\n" + block + "\n"
    if new == content:
        print(f"README up to date ({len(problems)} problems).")
        return 0
    with open(README, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"README updated ({len(problems)} problems).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
