package main

import (
	"fmt"
	"strings"
)

// 6. Zigzag Conversion  (https://leetcode.com/problems/zigzag-conversion/)
// write your solution between the markers below (submit.py sends this)
// LC-START
func convert(s string, numRows int) string {
	if numRows == 1 || numRows >= len(s) {
		return s
	}

	rows := make([]string, numRows)
	curRow := 0
	goingDown := false

	for _, c := range s {
		rows[curRow] += string(c)
		if curRow == 0 || curRow == numRows-1 {
			goingDown = !goingDown
		}
		if goingDown {
			curRow++
		} else {
			curRow--
		}
	}

	result := strings.Builder{}
	for _, row := range rows {
		result.WriteString(row)
	}
	return result.String()
}

// LC-END

func main() {
	cases := []struct {
		s       string
		numRows int
		want    string
	}{
		{"PAYPALISHIRING", 3, "PAHNAPLSIIGYIR"},
		{"PAYPALISHIRING", 4, "PINALSIGYAHRPI"},
		{"A", 1, "A"},
	}

	for i, c := range cases {
		got := convert(c.s, c.numRows)
		mark := "PASS"
		if !(got == c.want) {
			mark = "FAIL"
		}
		fmt.Printf("case %d: %s  got=%v want=%v\n", i+1, mark, got, c.want)
	}
}
