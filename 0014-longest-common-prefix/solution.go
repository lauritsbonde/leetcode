package main

import "fmt"

// 14. Longest Common Prefix  (https://leetcode.com/problems/longest-common-prefix/)
// write your solution between the markers below (submit.py sends this)
// LC-START
type Node struct {
	Char     string
	Children [26]*Node
	InWords  int8
}

func newNode(char string) *Node {
	node := &Node{
		Char:    char,
		InWords: 1,
	}
	return node
}

func (n *Node) OneChild() int {
	nonNil := 0
	childIndex := -1
	for i, child := range n.Children {
		if child != nil {
			nonNil += 1
			childIndex = i
			if nonNil > 1 {
				return -1
			}
		}
	}

	if nonNil == 0 {
		return -1
	}

	return childIndex
}

type Trie struct {
	RootNode *Node
}

func NewTrie() *Trie {
	root := newNode("\000")
	return &Trie{RootNode: root}
}

func (t *Trie) InsertWord(word string) error {
	current := t.RootNode

	for _, char := range word {
		index := char - 'a'

		if current.Children[index] == nil {
			current.Children[index] = newNode(string(char))
			current = current.Children[index]
		} else {
			current.Children[index].InWords++
			current = current.Children[index]
		}
	}
	return nil
}

func (t *Trie) LongestCommonPrefix(words int) string {
	currentPrefix := ""
	currentNode := t.RootNode

	childIndex := t.RootNode.OneChild()

	for childIndex != -1 && currentNode.Children[childIndex].InWords == int8(words) {
		currentNode = currentNode.Children[childIndex]
		childIndex = currentNode.OneChild()
		currentPrefix += currentNode.Char
	}
	return currentPrefix
}

func longestCommonPrefix(strs []string) string {
	trie := NewTrie()

	for _, word := range strs {
		trie.InsertWord(word)
	}

	return trie.LongestCommonPrefix(len(strs))
}

// LC-END

func main() {
	cases := []struct {
		strs []string
		want string
	}{
		{[]string{"flower", "flow", "flight"}, "fl"},
		{[]string{"dog", "racecar", "car"}, ""},
		{[]string{"", "b"}, ""},
		{[]string{"ab", "a"}, "a"},
	}

	for i, c := range cases {
		got := longestCommonPrefix(c.strs)
		mark := "PASS"
		if !(got == c.want) {
			mark = "FAIL"
		}
		fmt.Printf("case %d: %s  got=%v want=%v\n", i+1, mark, got, c.want)
	}
}
