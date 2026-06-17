package main

import "fmt"

// 2. Add Two Numbers  (https://leetcode.com/problems/add-two-numbers/)
// write your solution between the markers below (submit.py sends this)
type ListNode struct {
	Val  int
	Next *ListNode
}

// LC-START
/**
 * Definition for singly-linked list.
 * type ListNode struct {
 *     Val int
 *     Next *ListNode
 * }
 */

func addTwoNumbers(l1 *ListNode, l2 *ListNode) *ListNode {
	dummy := &ListNode{}
	current := dummy
	carry := 0

	for l1 != nil || l2 != nil || carry > 0 {
		sum := carry
		if l1 != nil {
			sum += l1.Val
			l1 = l1.Next
		}
		if l2 != nil {
			sum += l2.Val
			l2 = l2.Next
		}

		carry = sum / 10
		current.Next = &ListNode{Val: sum % 10}
		current = current.Next
	}

	return dummy.Next
}

// LC-END

func main() {
	// TODO: call the solution and print results
	fmt.Println("2. Add Two Numbers")
}
