package main

import (
	"fmt"
	"strings"
)

func ensureLeadingSlash(s string) string {
	if strings.HasPrefix(s, "/") {
		return s
	}
	return "/" + s
}

func main() {
	str1 := "/testPath"
	str2 := "testPath/pattt"

	fmt.Println(ensureLeadingSlash(str1)) // 输出: /testPath
	fmt.Println(ensureLeadingSlash(str2)) // 输出: /testPath
}
