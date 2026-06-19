package main

import "fmt"

// 12. Integer to Roman  (https://leetcode.com/problems/integer-to-roman/)
// write your solution between the markers below (submit.py sends this)
// LC-START
var lookupMap = map[int]string{
	1:    "I",
	4:    "IV",
	5:    "V",
	9:    "IX",
	10:   "X",
	40:   "XL",
	50:   "L",
	90:   "XC",
	100:  "C",
	400:  "CD",
	500:  "D",
	900:  "CM",
	1000: "M",
}

func intToRoman(num int) string {
	thousands := num / 1000
	hundreds := (num - 1000*thousands) / 100
	tens := (num - 1000*thousands - 100*hundreds) / 10
	ones := num - 1000*thousands - 100*hundreds - 10*tens

	fmt.Println(thousands, hundreds, tens, ones)
	return ""
}

// LC-END

func main() {
	cases := []struct {
		num  int
		want string
	}{
		{3749, "MMMDCCXLIX"},
		{58, "LVIII"},
		{1994, "MCMXCIV"},
	}

	for i, c := range cases {
		fmt.Printf("case %d: %v\n", i+1, intToRoman(c.num))
	}
}
