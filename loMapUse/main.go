package main

import (
	"fmt"
	"strings"
)

func main() {
	matches := []Match{{Version: "0.0.1"}, {Version: "0.0.2"}}
	fmt.Println("matchs", matches)
	matches = Map(matches, func(item Match, index int) Match {
		item.Version = strings.Replace(item.Version, ".", "-", -1)
		return item
	})
	fmt.Println("matchs", matches)
}

func Map[T any, R any](collection []T, iteratee func(item T, index int) R) []R {
	result := make([]R, len(collection))

	for i, item := range collection {
		result[i] = iteratee(item, i)
	}
	return result
}

type Match struct {
	Version string `json:"version"`
}
