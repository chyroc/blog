package main

import (
	"bytes"
	"io/ioutil"
	"sort"
	"text/template"

	"github.com/chyroc/blog/generate-index/internal"
)

func main() {
	dir := "src/posts"
	fs, err := ioutil.ReadDir(dir)
	assert(err)

	sort.Slice(fs, func(i, j int) bool {
		return fs[i].Name() > fs[j].Name()
	})

	posts := []*post{}
	for _, f := range fs {
		bs, err := ioutil.ReadFile(dir + "/" + f.Name())
		assert(err)
		_, meta, err := internal.ParseMarkdownMeta(string(bs))
		assert(err)
		if meta["draft"] == "" {
			posts = append(posts, &post{Name: meta["title"], Plug: meta["slug"], Path: f.Name()})
		}
	}

	index := buildTemplate(indexTemplate, posts)
	err = ioutil.WriteFile("./src/index.md", []byte(index), 0666)
	assert(err)
}

type post struct {
	Name string
	Plug string
	Path string
}

func assert(err error) {
	if err != nil {
		panic(err)
	}
}

func buildTemplate(templateContent string, data interface{}) string {
	t, err := template.New("").Parse(templateContent)
	if err != nil {
		panic(err)
	}
	buf := new(bytes.Buffer)
	err = t.Execute(buf, data)
	if err != nil {
		panic(err)
	}
	return buf.String()
}

var indexTemplate = `--
title: "博客 | chyroc"
slug: "index"
--
# 博客 | chyroc

> Homepage: [https://chyroc.cn/](https://chyroc.cn/)

### 博客

{{range .}}- [{{.Name}}](./posts/{{.Path}})
{{end}}

## 关于本博客

* 博客的生成：[mdcat](https://github.com/chyroc/mdcat)
* TODO: 基于 Issue 的博客评论系统：[gitment](https://github.com/imsun/gitment)

### 友链

- [laike9m's blog](https://laike9m.com/)
`
