all: build

build:
	hugo

push:
	 git commit -a -m update && git push
