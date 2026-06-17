#!/usr/bin/env python3
"""Submit a local solution to LeetCode.

Usage:
    python3 submit.py 0001-two-sum            # auto-detect the solution file
    python3 submit.py 0001-two-sum go         # pick a language explicitly

Auth (grab from a logged-in browser, DevTools > Application > Cookies):
    export LEETCODE_SESSION="..."
    export LEETCODE_CSRF="..."        # the csrftoken cookie value
or put them in a .lc-cookies.json next to this script:
    {"LEETCODE_SESSION": "...", "LEETCODE_CSRF": "..."}
"""

import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRAPHQL = "https://leetcode.com/graphql"
BASE = "https://leetcode.com"

# file ext -> LeetCode langSlug
EXT_TO_LANG = {
    "go": "golang",
    "py": "python3",
    "cpp": "cpp",
    "java": "java",
    "js": "javascript",
    "ts": "typescript",
    "rs": "rust",
}


def load_cookies():
    sess = os.environ.get("LEETCODE_SESSION")
    csrf = os.environ.get("LEETCODE_CSRF")
    cfg = HERE / ".lc-cookies.json"
    if (not sess or not csrf) and cfg.exists():
        data = json.loads(cfg.read_text())
        sess = sess or data.get("LEETCODE_SESSION")
        csrf = csrf or data.get("LEETCODE_CSRF")
    if not sess or not csrf:
        sys.exit(
            "Missing auth. Set LEETCODE_SESSION + LEETCODE_CSRF env vars "
            "or create .lc-cookies.json (see --help)."
        )
    return sess, csrf


def auth_headers(sess, csrf, slug):
    return {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "x-csrftoken": csrf,
        "Referer": f"{BASE}/problems/{slug}/",
        "Origin": BASE,
        "Cookie": f"LEETCODE_SESSION={sess}; csrftoken={csrf}",
    }


def http(url, headers, data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers,
                                 method="POST" if data is not None else "GET")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def question_id(slug, headers):
    q = """query q($titleSlug: String!) {
      question(titleSlug: $titleSlug) { questionId }
    }"""
    data = http(GRAPHQL, headers, {"query": q, "variables": {"titleSlug": slug}})
    return data["data"]["question"]["questionId"]


def find_solution(dirpath, want_ext=None):
    sols = sorted(dirpath.glob("solution.*"))
    if not sols:
        sys.exit(f"No solution.* in {dirpath}")
    if want_ext:
        for s in sols:
            if s.suffix.lstrip(".") == want_ext:
                return s
        sys.exit(f"No solution.{want_ext} in {dirpath}")
    if len(sols) > 1:
        names = ", ".join(s.name for s in sols)
        sys.exit(f"Multiple solutions ({names}); pass a language, e.g. 'go'")
    return sols[0]


def extract_code(text):
    """Return the code between LC-START / LC-END, else the whole file."""
    m = re.search(r"LC-START\s*\n(.*?)\n[^\n]*LC-END", text, flags=re.S)
    return (m.group(1) if m else text).strip("\n")


def submit(slug, qid, lang, code, headers):
    payload = {"lang": lang, "question_id": str(qid), "typed_code": code}
    resp = http(f"{BASE}/problems/{slug}/submit/", headers, payload)
    sid = resp.get("submission_id")
    if not sid:
        sys.exit(f"Submit failed: {resp}")
    return sid


def poll(sid, headers):
    url = f"{BASE}/submissions/detail/{sid}/check/"
    for _ in range(60):
        r = http(url, headers)
        if r.get("state") == "SUCCESS":
            return r
        time.sleep(1)
    sys.exit("Timed out waiting for judge result")


def report(r):
    status = r.get("status_msg", "Unknown")
    print(f"\n=== {status} ===")
    if r.get("status_code") == 10:  # accepted
        print(f"Runtime: {r.get('status_runtime')}  "
              f"({r.get('runtime_percentile', 0):.1f}%)")
        print(f"Memory:  {r.get('status_memory')}  "
              f"({r.get('memory_percentile', 0):.1f}%)")
        print(f"Passed:  {r.get('total_correct')}/{r.get('total_testcases')}")
        return 0
    # failures
    if r.get("total_correct") is not None:
        print(f"Passed: {r.get('total_correct')}/{r.get('total_testcases')}")
    if r.get("last_testcase"):
        print(f"Last input:  {r['last_testcase']!r}")
        print(f"Expected:    {r.get('expected_output')!r}")
        print(f"Got:         {r.get('code_output')!r}")
    if r.get("full_compile_error"):
        print(r["full_compile_error"])
    elif r.get("runtime_error"):
        print(r["runtime_error"])
    return 1


def record_solved(dirpath, lang, sid, r):
    """Persist an Accepted verdict to <dir>/.solved.json (one entry per lang).

    This file is the source of truth for 'solved' — stats.py reads it to build
    the progress page. Commit it alongside your solution.
    """
    rec_path = dirpath / ".solved.json"
    rec = {"slug": dirpath.name.split("-", 1)[1], "solutions": {}}
    if rec_path.exists():
        try:
            rec = json.loads(rec_path.read_text())
            rec.setdefault("solutions", {})
        except (json.JSONDecodeError, OSError):
            pass
    rec["solutions"][lang] = {
        "runtime": r.get("status_runtime"),
        "runtime_pct": round(r.get("runtime_percentile", 0) or 0, 1),
        "memory": r.get("status_memory"),
        "memory_pct": round(r.get("memory_percentile", 0) or 0, 1),
        "submission_id": sid,
        "date": time.strftime("%Y-%m-%d"),
    }
    rec_path.write_text(json.dumps(rec, indent=2) + "\n")
    print(f"Recorded Accepted ({lang}) in {rec_path.name} — commit it to update the page.")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    dirpath = (HERE / "problems" / sys.argv[1]).resolve()
    if not dirpath.is_dir():
        sys.exit(f"Not a directory: {dirpath}")
    want_ext = sys.argv[2].lstrip(".") if len(sys.argv) > 2 else None
    if want_ext in ("python", "python3"):
        want_ext = "py"

    sol = find_solution(dirpath, want_ext)
    ext = sol.suffix.lstrip(".")
    lang = EXT_TO_LANG.get(ext)
    if not lang:
        sys.exit(f"Unknown language for .{ext}")

    slug = dirpath.name.split("-", 1)[1]  # 0001-two-sum -> two-sum
    code = extract_code(sol.read_text())

    sess, csrf = load_cookies()
    headers = auth_headers(sess, csrf, slug)

    print(f"Submitting {sol.name} ({lang}) to '{slug}' ...")
    qid = question_id(slug, headers)
    sid = submit(slug, qid, lang, code, headers)
    print(f"submission_id={sid}, waiting for judge ...")
    r = poll(sid, headers)
    rc = report(r)
    if r.get("status_code") == 10:  # accepted
        record_solved(dirpath, lang, sid, r)
    sys.exit(rc)


if __name__ == "__main__":
    main()
