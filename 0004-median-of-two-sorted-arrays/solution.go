package main

import "fmt"

// 4. Median of Two Sorted Arrays  (https://leetcode.com/problems/median-of-two-sorted-arrays/)
// write your solution between the markers below (submit.py sends this)
// LC-START
func findMedianSortedArrays(nums1 []int, nums2 []int) float64 {
	m, n := len(nums1), len(nums2)
	merged := make([]int, 0, m+n)
	i, j := 0, 0

	// Merge the two sorted arrays
	for i < m && j < n {
		if nums1[i] < nums2[j] {
			merged = append(merged, nums1[i])
			i++
		} else {
			merged = append(merged, nums2[j])
			j++
		}
	}
	for i < m {
		merged = append(merged, nums1[i])
		i++
	}
	for j < n {
		merged = append(merged, nums2[j])
		j++
	}

	total := m + n
	if total%2 == 1 {
		return float64(merged[total/2])
	}
	return float64(merged[total/2-1]+merged[total/2]) / 2.0
}

// LC-END

func main() {
	cases := []struct {
		nums1 []int
		nums2 []int
		want  float64
	}{
		{[]int{1, 3}, []int{2}, 2.0},
		{[]int{1, 2}, []int{3, 4}, 2.5},
	}

	for i, c := range cases {
		got := findMedianSortedArrays(c.nums1, c.nums2)
		mark := "PASS"
		if !(got == c.want) {
			mark = "FAIL"
		}
		fmt.Printf("case %d: %s  got=%v want=%v\n", i+1, mark, got, c.want)
	}
}
