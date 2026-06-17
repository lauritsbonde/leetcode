package main

import "fmt"

// 3. Longest Substring Without Repeating Characters  (https://leetcode.com/problems/longest-substring-without-repeating-characters/)
// write your solution between the markers below (submit.py sends this)
// LC-START
func lengthOfLongestSubstring(s string) int {
	hashMap := make(map[rune]int)
	maxLength := 0
	start := 0

	for i, char := range s {
		if index, found := hashMap[char]; found && index >= start {
			start = index + 1
		}
		hashMap[char] = i
		if i-start+1 > maxLength {
			maxLength = i - start + 1
		}
	}
	return maxLength
}

// LC-END

func main() {
	cases := []struct {
		s    string
		want int
	}{
		{"abcabcbb", 3},
		{"bbbbb", 1},
		{"pwwkew", 3},
	}

	for i, c := range cases {
		got := lengthOfLongestSubstring(c.s)
		mark := "PASS"
		if !(got == c.want) {
			mark = "FAIL"
		}
		fmt.Printf("case %d: %s  got=%v want=%v\n", i+1, mark, got, c.want)
	}
}
