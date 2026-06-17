package main

import (
	"fmt"
	"math"
)

// 8. String to Integer (atoi)  (https://leetcode.com/problems/string-to-integer-atoi/)
// write your solution between the markers below (submit.py sends this)
// LC-START
func myAtoi(s string) int {
	n := len(s)
	i := 0
	sign := 1
	res := 0

	// 1. Skip leading whitespace
	for i < n && s[i] == ' ' {
		i++
	}

	// 2. Handle sign
	if i < n {
		if s[i] == '-' {
			sign = -1
			i++
		} else if s[i] == '+' {
			i++
		}
	}

	// 3. Process digits
	for i < n && s[i] >= '0' && s[i] <= '9' {
		digit := int(s[i] - '0')

		// 4. Check for overflow
		if res > math.MaxInt32/10 || (res == math.MaxInt32/10 && digit > 7) {
			if sign == 1 {
				return math.MaxInt32
			} else {
				return math.MinInt32
			}
		}

		res = res*10 + digit
		i++
	}

	return res * sign
}

// LC-END

func main() {
	cases := []struct {
		s string
	}{
		{"42"},
		{"   -042"},
		{"1337c0d3"},
		{"0-1"},
		{"words and 987"},
	}

	for i, c := range cases {
		fmt.Printf("case %d: %v\n", i+1, myAtoi(c.s))
	}
}
