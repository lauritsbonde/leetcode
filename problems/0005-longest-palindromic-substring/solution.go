package main

import "fmt"

// 5. Longest Palindromic Substring  (https://leetcode.com/problems/longest-palindromic-substring/)
// write your solution between the markers below (submit.py sends this)
// LC-START
func longestPalindrome(s string) string {
	if len(s) == 0 {
		return ""
	}

	start, end := 0, 0

	exploreFromMiddle := func(left, right int) {
		for left >= 0 && right < len(s) && s[left] == s[right] {
			if right-left+1 > end-start+1 {
				start = left
				end = right
			}
			left--
			right++
		}
	}

	for i := range s {
		exploreFromMiddle(i, i)

		exploreFromMiddle(i, i+1)
	}

	return s[start : end+1]
}

func longestPalindromeDP(s string) string {
	n := len(s)
	if n == 0 {
		return ""
	}

	dp := make([][]bool, n)
	for i := range dp {
		dp[i] = make([]bool, n)
		dp[i][i] = true
	}

	start, maxLen := 0, 1

	// Check substrings of length 2
	for i := 0; i < n-1; i++ {
		if s[i] == s[i+1] {
			dp[i][i+1] = true
			start = i
			maxLen = 2
		}
	}

	// Check substrings of length > 2
	for length := 3; length <= n; length++ {
		for i := 0; i <= n-length; i++ {
			j := i + length - 1
			if s[i] == s[j] && dp[i+1][j-1] {
				dp[i][j] = true
				if length > maxLen {
					start = i
					maxLen = length
				}
			}
		}
	}

	return s[start : start+maxLen]
}

// LC-END

func main() {
	cases := []struct {
		s    string
		want string
	}{
		{"babad", "bab"},
		{"cbbd", "bb"},
	}

	for i, c := range cases {
		got := longestPalindrome(c.s)
		mark := "PASS"
		if !(got == c.want) {
			mark = "FAIL"
		}
		fmt.Printf("case %d: %s  got=%v want=%v\n", i+1, mark, got, c.want)
	}
}
