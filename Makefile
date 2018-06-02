all: build

build:
	rm -rf public
	hugo

push:
	git commit -a -m update && git push
