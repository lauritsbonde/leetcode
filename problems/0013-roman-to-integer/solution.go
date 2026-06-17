package main

import "fmt"

// 13. Roman to Integer  (https://leetcode.com/problems/roman-to-integer/)
// write your solution between the markers below (submit.py sends this)
// LC-START

var lookupMap = map[string]int{
	"I":  1,
	"IV": 4,
	"V":  5,
	"IX": 9,
	"X":  10,
	"XL": 40,
	"L":  50,
	"XC": 90,
	"C":  100,
	"CD": 400,
	"D":  500,
	"CM": 900,
	"M":  1000,
}

func romanToInt(s string) int {
	sum := 0
	length := len(s)
	for i := 0; i < length; i++ {
		if i+1 < length {
			doubleKey := string(s[i]) + string(s[i+1])
			double, ok := lookupMap[doubleKey]
			if ok {
				sum += double
				i++
				continue
			}
		}
		single, _ := lookupMap[string(s[i])]
		sum += single
	}
	return sum
}

// LC-END

func main() {
	cases := []struct {
		s    string
		want int
	}{
		{"III", 3},
		{"LVIII", 58},
		{"MCMXCIV", 1994},
	}

	for i, c := range cases {
		got := romanToInt(c.s)
		mark := "PASS"
		if !(got == c.want) {
			mark = "FAIL"
		}
		fmt.Printf("case %d: %s  got=%v want=%v\n", i+1, mark, got, c.want)
	}
}
