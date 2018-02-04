# slice与底层数组引用

- time 2018-01-25
- from https://github.com/goquiz/goquiz.github.io

```go
package main

import (
	"fmt"
)

func main() {
	s := []int{1, 2, 3}
	ss := s[1:]
	for i := range ss {
		ss[i] += 10
	}
	fmt.Println(s)
	ss = append(ss, 4)
	for i := range ss {
		ss[i] += 10
	}
	fmt.Println(s)
}
```

结果是
```
[1 12 13]
[1 12 13]
```

也就是说第一个循环改变了s，第二个循环没有改变。

为什么会这样呢，因为在第一个循环中，s和ss都是slice，底层共用的是一个数组，所以改变ss的时候，实际上改变的是底层的数组，所以s也会跟着改变。

在第二个循环中，`ss = append(ss, 4)`这句话会将ss底层引用的数组改变，所以从这里开始s和ss就没有关联了。所以改变ss的时候，并不会改变s。

可以打印出slice的底层数组印证一下：

```go
package main

import (
	"fmt"
	"reflect"
	"unsafe"
)

func printArrayOfSlice(msg string, s []int) {
	hdr := (*reflect.SliceHeader)(unsafe.Pointer(&s))
	data := *(*[3]int)(unsafe.Pointer(hdr.Data))
	fmt.Printf("%s \tarray\t%+v\n", msg, data)
}

func main() {
	s := []int{1, 2, 3}
	ss := s[1:]
	for i := range ss {
		ss[i] += 10
	}
	printArrayOfSlice("s", s)
	printArrayOfSlice("ss", ss)

	ss = append(ss, 4)
	for i := range ss {
		ss[i] += 10
	}
	printArrayOfSlice("s", s)
	printArrayOfSlice("ss", ss)
}
```

结果是
```
s 	array	[1 12 13]
ss 	array	[12 13 842350739296]
s 	array	[1 12 13]
ss 	array	[22 23 14]
```

说明的我的想法：ss在前后所引用底层数组改变了。