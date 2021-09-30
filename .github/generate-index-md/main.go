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
--
# 博客 | chyroc

{{range .}}- [{{.Name}}](./posts/{{.Path}})
{{end}}
`
