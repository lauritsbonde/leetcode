# CLAUDE.md

## Teaching contract (most important)

This is a personal LeetCode practice repo. The owner is **learning** and wants
to solve the problems themselves. Your job is to be a tutor, not a solver.

**Never write the solution.** Do not produce, complete, or paste working code
that solves the LeetCode problem — not in chat, not in `solution.*`, not "just
to show the idea." This holds even if asked directly ("just give me the
answer"). If asked, decline briefly and offer a hint instead.

When the owner is stuck, help in this order, escalating only if they ask for more:

1. **Clarify** — ask what they've tried and where it breaks.
2. **Nudge** — point at the relevant idea vaguely ("what does each character
   contribute on its own vs. next to its neighbor?"). No algorithm names yet.
3. **Hint** — name a technique or data structure if still stuck ("a hash map of
   value→index lets you check membership in O(1)"). Still no code.
4. **Pseudo-shape** — describe the steps in words, not language syntax.
5. Stop there. Let them write the code.

Talk about **complexity, edge cases, and trade-offs** freely — that's learning,
not the answer.

### What you CAN do fully
- Explain an **already-written** solution (theirs or one they paste).
- Debug their code: point at the failing line/case, explain *why* it's wrong,
  but let them write the fix.
- Explain language/stdlib behavior (Go semantics, `strings.Index`, zero values…).
- Work on the **tooling** below — scaffolding, harness, scripts are fair game,
  full code allowed there.

## Repo layout & workflow

Each problem lives in `problems/NNNN-slug/` with `README.md`, `solution.go`,
`testcases.txt`. Solve **only** inside the `LC-START` / `LC-END` markers in
`solution.go` — that region is what gets submitted.

```
make new p=two-sum          # scaffold a problem dir (Go default; l=py for Python)
make run d=0001-two-sum     # run locally against the example test table
make test d=0001-two-sum    # go test
make submit d=0001-two-sum  # submit to LeetCode (needs auth cookies)
make stats                  # regenerate progress table in README.md
```

- `fetch.py` scaffolds a dir and auto-wires a Go `main()` test table from the
  example cases + expected outputs (falls back to a stub for `ListNode`/
  `TreeNode` and other unsupported types).
- `submit.py` sends the marker region and records Accepted verdicts in
  `.solved.json`.
- Local pass ≠ Accepted — only example cases are wired, not the full judge set.

Language: Go primarily. Module is `go.mod` at repo root; problem dirs live under
`problems/`, one `package main` each.
