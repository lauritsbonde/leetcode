package main

import (
	"fmt"
	"strconv"
)

// 9. Palindrome Number  (https://leetcode.com/problems/palindrome-number/)
// write your solution between the markers below (submit.py sends this)
// LC-START
func isPalindrome(x int) bool {
	str := strconv.Itoa(x)
	length := len(str)
	halfLength := length / 2
	for i, n := range str {
		if i > halfLength {
			return true
		}
		if n != rune(str[length-i-1]) {
			return false
		}
	}
	return true
}

// LC-END

func main() {
	cases := []struct {
		in   int
		want bool
	}{
		{121, true},
		{-121, false},
		{10, false},
	}
	for _, c := range cases {
		got := isPalindrome(c.in)
		status := "PASS"
		if got != c.want {
			status = "FAIL"
		}
		fmt.Printf("%s  isPalindrome(%d) = %v, want %v\n", status, c.in, got, c.want)
	}
}
