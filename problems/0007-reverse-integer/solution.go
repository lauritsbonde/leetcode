package main

import (
	"fmt"
	"math"
	"strconv"
)

// 7. Reverse Integer  (https://leetcode.com/problems/reverse-integer/)
// write your solution between the markers below (submit.py sends this)
// LC-START
func reverse(x int) int {
	stringified := strconv.Itoa(x)

	isSigned := x < 0
	isStarted := false
	skippedNumbers := 0

	res := make([]byte, len(stringified))

	for c := range stringified {
		if isSigned && c == 0 {
			skippedNumbers++
			continue
		}
		if stringified[c] == 0 && isStarted == false {
			skippedNumbers++
			continue
		}
		isStarted = true
		res[len(stringified)-1-c] = stringified[c]
	}

	reversedString := string(res[:len(res)-skippedNumbers])
	parsed, err := strconv.Atoi(reversedString)
	if err != nil || parsed > math.MaxInt32 {
		return 0
	}
	if isSigned {
		return parsed * -1
	}
	return parsed
}

// LC-END

func main() {
	cases := []struct {
		x    int
		want int
	}{
		{123, 321},
		{-123, -321},
		{120, 21},
	}

	for i, c := range cases {
		got := reverse(c.x)
		mark := "PASS"
		if !(got == c.want) {
			mark = "FAIL"
		}
		fmt.Printf("case %d: %s  got=%v want=%v\n", i+1, mark, got, c.want)
	}
}
