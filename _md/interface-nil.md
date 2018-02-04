# interface与nil的比较

- time 2018-01-25
- from https://github.com/goquiz/goquiz.github.io

```go
package main

type S struct{}

func (s S) F() {}

type IF interface {
	F()
}

func InitType() S {
	var s S
	return s
}

func InitPointer() *S {
	var s *S
	return s
}
func InitEfaceType() interface{} {
	var s S
	return s
}

func InitEfacePointer() interface{} {
	var s *S
	return s
}

func InitIfaceType() IF {
	var s S
	return s
}

func InitIfacePointer() IF {
	var s *S
	return s
}

func main() {
	//println(InitType() == nil)
	println(InitPointer() == nil)
	println(InitEfaceType() == nil)
	println(InitEfacePointer() == nil)
	println(InitIfaceType() == nil)
	println(InitIfacePointer() == nil)
}

```

结果是

```
// cannot convert nil to type S
true
false
false
false
false
```

第一个`cannot convert nil to type S`是？

true是因为函数返回的是指针类型，指针类型的零值是nil

后面的结果都是false的原因是：后面的函数返回的结果都是interface，而一个interface如果想要等于nil的话，那么它的`类型`和`值`都必须等于nil，也就是说必须明确的返回nil才可以。但是这些函数都是返回来了含有类型的interface，所以不等于nil。

参见：[go - Expecting nil but getting an interface with a nil value in return, which should be nil - Stack Overflow](https://stackoverflow.com/questions/26845572/expecting-nil-but-getting-an-interface-with-a-nil-value-in-return-which-should)