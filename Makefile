all: build

generate-index-md:
	cd .github/generate-index-md && go build -o /tmp/blog-generate-index-md main.go
	/tmp/blog-generate-index-md

generate-html:
	mdcat --config ./src/config.yaml src/index.md

build:
	make generate-index-md
	make generate-html