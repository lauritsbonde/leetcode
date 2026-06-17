# LeetCode

My LeetCode solutions, one directory per problem. Each problem is scaffolded by `fetch.py`.
Root is a single Go module (`go.mod`); every problem dir is its own `package main`.

📊 **[Progress page](https://lauritsbonde.github.io/leetcode/)** — auto-updated table of every solved problem (counts, languages, topics). Built by CI on each push to `main` and published to the `gh-pages` branch; `main` stays commit-clean.

## Scaffold a problem

```sh
make new p=two-sum          # by slug, default Go
make new p=two-sum l=py     # override language
```

Or call the script directly:

```sh
python3 fetch.py two-sum                              # by slug
python3 fetch.py https://leetcode.com/problems/two-sum/   # by url
python3 fetch.py 1                                    # by id (slower, paginates)
python3 fetch.py two-sum py                           # override language
```

Creates `problems/0001-two-sum/` with:

| File             | What                                            |
|------------------|-------------------------------------------------|
| `README.md`      | Title, difficulty, topics, link, description    |
| `solution.<ext>` | Starter stub (default Go, override via 2nd arg) |
| `testcases.txt`  | Sample test inputs                              |

Stdlib only — no `pip install`. Uses the LeetCode GraphQL API. Re-running won't overwrite an existing `solution.*`, so fetching the same problem in another language adds a second `solution.<ext>` alongside the first.

### Languages

Default `go`. Override with 2nd arg: `go`, `py`/`python`/`python3`, `cpp`, `java`, `js`, `ts`, `rust`.

## Run

```sh
make run d=0001-two-sum     # go run ./problems/0001-two-sum
make test d=0001-two-sum    # go test ./problems/0001-two-sum
make py d=0001-two-sum      # python3 ./problems/0001-two-sum/solution.py
make fmt d=0001-two-sum     # gofmt -w
make vet d=0001-two-sum     # go vet
```

**Note:** the fresh Go stub has an empty function body, so `go run` fails with `missing return` until you write the solution (or give it a temp `return nil`). That is LeetCode's default snippet, not a harness bug.

## Submit

Submit a local solution straight to LeetCode.

```sh
make submit d=0001-two-sum        # auto-detects the solution file
make submit d=0001-two-sum l=go   # pick a language if a dir has several
```

Prints the judge result: runtime/memory + percentiles on Accepted, or the failing
testcase (expected vs got) / compile error otherwise.

### Auth (once)

LeetCode has no public submit API, so it uses your browser session cookies.
DevTools → Application → Cookies → `leetcode.com`, copy `LEETCODE_SESSION` and
`csrftoken`. Either set env vars:

```sh
export LEETCODE_SESSION="..."
export LEETCODE_CSRF="..."        # the csrftoken value
```

or create `.lc-cookies.json` (gitignored):

```json
{"LEETCODE_SESSION": "...", "LEETCODE_CSRF": "..."}
```

Cookies expire — re-grab when submit starts failing auth. Automating submits is
against LeetCode's ToS; your account, your call.

### Markers

Only the code between the `LC-START` / `LC-END` comment markers is submitted — this
strips the local `package main` / `func main()` harness so LeetCode gets just the
snippet. Keep your solution inside the markers. If a dir was fetched before markers
existed, re-fetch it (won't clobber an existing `solution.*` of another language —
delete the file first if you want it regenerated).

## Layout

```
leetcode/
├── README.md
├── Makefile
├── go.mod
├── fetch.py            # scaffold a problem
├── submit.py           # submit a solution
├── .lc-cookies.json    # auth (gitignored)
└── problems/
    └── 0001-two-sum/
        ├── README.md
        ├── solution.go
        └── testcases.txt
```

Problem dirs live under `problems/`, named `<4-digit-id>-<slug>` so they sort by problem number.

## Progress

<!-- STATS:START -->

**Solved: 11** &nbsp; | &nbsp; 🟢 Easy 4 &nbsp; · &nbsp; 🟡 Medium 6 &nbsp; · &nbsp; 🔴 Hard 1

| # | Problem | Difficulty | Languages | Runtime | Topics |
|---|---------|------------|-----------|---------|--------|
| 1 | [1. Two Sum](https://leetcode.com/problems/two-sum/) | 🟢 Easy | Go | 0 ms | Array, Hash Table |
| 2 | [2. Add Two Numbers](https://leetcode.com/problems/add-two-numbers/) | 🟡 Medium | Go | 0 ms | Linked List, Math, Recursion |
| 3 | [3. Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | 🟡 Medium | Go | 0 ms | Hash Table, String, Sliding Window |
| 4 | [4. Median of Two Sorted Arrays](https://leetcode.com/problems/median-of-two-sorted-arrays/) | 🔴 Hard | Go | 0 ms | Array, Binary Search, Divide and Conquer |
| 5 | [5. Longest Palindromic Substring](https://leetcode.com/problems/longest-palindromic-substring/) | 🟡 Medium | Go | 3 ms | Two Pointers, String, Dynamic Programming |
| 6 | [6. Zigzag Conversion](https://leetcode.com/problems/zigzag-conversion/) | 🟡 Medium | Go | 10 ms | String |
| 7 | [7. Reverse Integer](https://leetcode.com/problems/reverse-integer/) | 🟡 Medium | Go | 6 ms | Math |
| 8 | [8. String to Integer (atoi)](https://leetcode.com/problems/string-to-integer-atoi/) | 🟡 Medium | Go | 0 ms | String |
| 9 | [9. Palindrome Number](https://leetcode.com/problems/palindrome-number/) | 🟢 Easy | Go | 0 ms | Math |
| 13 | [13. Roman to Integer](https://leetcode.com/problems/roman-to-integer/) | 🟢 Easy | Go | 0 ms | Hash Table, Math, String |
| 14 | [14. Longest Common Prefix](https://leetcode.com/problems/longest-common-prefix/) | 🟢 Easy | Go | 0 ms | Array, String, Trie |

<!-- STATS:END -->
