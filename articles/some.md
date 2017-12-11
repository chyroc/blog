目前做的一个业务涉及到`websocket`，在这里记录下来，虽然还不知道那个pr会不会过。

整个业务可以概括为：
> 涉及到三端：前端、后端和第三方服务商

> 前端发起一个请求，会产生一个 `op_id`

>  第三方服务商在这个请求过程中，会不断`post`数据到后端提供的回调地址上

>  后端需要把这些信息以`websocket`的方式提供给前端，以做好交互

我大概想了一下，需要处理这么几个问题

- 用户验证（指`websocket`端的）
- 绑定用户和`op_id`，使得`websocket`消息可以到达指定用户
- 打开多个窗口，怎么保证收到的消息是一样的（同步）
- 数据怎么从回调 `goroutine`传递到另外一个`websocket goroutine`内

### 用户验证

`websocket`首先使用一个`get`请求建立连接，然后不再断开，可以在建立连接的时候进行身份认证
```json
{
    "method": "GET",
    "path": "/websocket/:access_token",
    "request": "GET /websocket/........ HTTP/1.1......Connection: Upgrade.....Upgrade: websocket....."
  }
```

### 数据绑定
我使用的方法是在前端`前端发起一个请求，会产生一个 op_id`的时候，将`op_id`和`user_id`存在redis里面

没有存变量/channel 是因为需要保证在一个通话过程中，重启服务端不会清除数据

### 多终端消息一致

使用全局变量clients存储连接，对于同一user的多个终端，遍历存起来的链接，每个都进行消息发送。

```go
func HandlerWebsocket(w http.ResponseWriter, r *http.Request) {
  // ... some code

	clients.Add(user, c)
	defer clients.Delete(userKey, c)

	for {
		if v, ok := message[user]; ok {
			message := <-v

			cls := clients.Get(user)
			for conn, _ := range cls { // 这里有循环对同一用户进行消息广播
				conn.WriteJSON(message)
			}
		}
	}
}
```

这是存储用户和链接的数据结构（简化版）。

这里有一个问题，指针可以作为key，而`websocket.Conn`不行，原因忘了，原来有一次看到过。
```go
map[string]map[*websocket.Conn]bool
```

### goroutine间数据传递

使用channel

```go
var message = make(map[string](chan map[string]interface{}))

func HandlerCallback(body CallbackBody) (int, string) {
	// ... some code

	message[user] <- body

	// ... some code
}

// 使用见前一小节
```
