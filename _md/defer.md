# defer与panic的问题（defer之二）

- time 2018-01-25
- from https://github.com/goquiz/goquiz.github.io

defer与panic问题
```go
package main

func f1() {
	defer println("f1-begin")
	f2()
	defer println("f1-end")
}

func f2() {
	defer println("f2-begin")
	f3()
	defer println("f2-end")
}

func f3() {
	defer println("f3-begin")
	panic(0)
	defer println("f3-end")
}

func main() {
	f1()
}
```

最后f3中panic，所以defer不再增加，defer栈是：`f11 f21 f31 panic`

第二个问题
```go
package main

import "log"

func f() {
	defer func() {
		if r := recover(); r != nil {
			log.Printf("recover:%#v", r)
		}
	}()
	panic(1)
	panic(2)
}

func main() {
	f()
}
```

两个panic的时候recover，结果是什么：

panic之后，要么直接退出函数，要么recover一下退出函数，不会再执行别的代码
