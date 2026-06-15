package main

import "fmt"

// 1. Two Sum  (https://leetcode.com/problems/two-sum/)
// write your solution between the markers below (submit.py sends this)
// LC-START
func twoSum(nums []int, target int) []int {
	seen := make(map[int]int)
	for i, n := range nums {
		other, ok := seen[target-n]
		if ok {
			return []int{other, i}
		} else {
			seen[n] = i
		}
	}
	return []int{}
}

// LC-END

func main() {
	// TODO: call the solution and print results
	fmt.Println("1. Two Sum")
	fmt.Println(twoSum([]int{2, 7, 11, 15}, 9))
}
