# defer与return的问题（defer之一）

- time 2018-01-25
- from https://github.com/goquiz/goquiz.github.io

[go-internals/03.4.md at master · tiancaiamao/go-internals · GitHub](https://github.com/tiancaiamao/go-internals/blob/master/zh/03.4.md)阅读有感

我们知道defer的时候会将后面的函数入栈，然后return的时候执行。

那么具体是什么样子的呢。

**最重要的一点就是要明白，return xxx这一条语句并不是一条原子指令!**

分三步：
```
- 将return后面的值计算出来，赋给t（这个t是函数声明中的变量）
- 执行defer函数
- 空的return（结果就是那个t）
```

下面这段代码给了三个使用了defer的函数`f_x()`，然后将其分解开了，写成了`g_x()`，希望通过这个分解让你对defer更加了解。

```go
package main

import "sync"

func f1() (result int) {
	defer func() {
		result++
	}()
	return 0
}

func g1() (result int) {
	result = 0 // 1
	result++   // 2
	return     // 3
}

func f2() (r int) {
	t := 5
	defer func() {
		t = t + 5
	}()
	return t
}

func g2() (r int) {
	t := 5

	r = t     // 1
	t = t + 5 // 2
	return    // 3
}

func f3() (r int) {
	defer func(r int) {
		r = r + 5
	}(r)
	return 1
}

func g3() (r int) {
	r = 1                                     // 1
	var s = sync.WaitGroup{}                  // 2
	s.Add(1)                                  // 2
	go func(r int) { r = r + 5; s.Done() }(r) // 2
	s.Wait()                                  // 2
	return                                    // 3
}

func main() {
	println(f1(), f1() == g1())
	println(f2(), f2() == g2())
	println(f3(), f3() == g3())
}
```

结果是
```
1 true
5 true
1 true
```
