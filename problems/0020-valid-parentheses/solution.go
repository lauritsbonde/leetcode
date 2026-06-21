package main

import "fmt"

// 20. Valid Parentheses  (https://leetcode.com/problems/valid-parentheses/)
// write your solution between the markers below (submit.py sends this)
// LC-START
type Stack struct {
	items []string
}

func (s *Stack) Push(data string) {
	s.items = append(s.items, data)
}

func (s *Stack) Pop() string {
	if s.IsEmpty() {
		return ""
	}
	item := s.items[len(s.items)-1]
	s.items = s.items[:len(s.items)-1]
	return item
}

func (s *Stack) IsEmpty() bool {
	if len(s.items) == 0 {
		return true
	}
	return false
}

var closers = map[string]string{
	")": "(",
	"]": "[",
	"}": "{",
}

func isValid(s string) bool {
	stack := Stack{}

	for _, n := range s {
		if opener, ok := closers[string(n)]; ok {
			if stack.Pop() != opener {
				return false
			}
		} else {
			stack.Push(string(n))
		}
	}
	return stack.IsEmpty()
}

// LC-END

func main() {
	cases := []struct {
		s        string
		expected bool
	}{
		{"()", true},
		{"()[]{}", true},
		{"(]", false},
		{"([])", true},
		{"([)]", false},
		{"[", false},
	}

	for i, c := range cases {
		fmt.Printf("case %d: got=%v want=%v\n", i+1, isValid(c.s), c.expected)
	}
}
