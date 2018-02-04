# for循环中index指针与变量作用域的问题

- time 2018-01-25
- from https://github.com/goquiz/goquiz.github.io

```go
package main

const N = 3

func main() {
	m := make(map[int]*int)

	for i := 0; i < N; i++ {
		m[i] = &i //A
	}

	for _, v := range m {
		print(*v)
	}
}

```

结果是
```
333
```

原因是
- 循环的k,v的地址在循环的时候是不变的
- 循环内声明的变量，每次都是不一样的
- 存k和v的地址并不会计算出来然后存起来，而是存的「k和v的地址」这个概念，所以最后所有的值指向的都是最后一次循环的地址

**所以重点就是i每次都是那个i，p每次都不是那个p（作用域知识）**

所以需要在循环内部申请局部变量存i，然后把他的地址赋给map
```go
package main

const N = 3

func main() {
	m := make(map[int]*int)

	for i := 0; i < N; i++ {
		p := i
		m[i] = &p //A
	}

	for _, v := range m {
		print(*v)
	}
}

```