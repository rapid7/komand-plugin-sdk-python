setup:
	make -C plugin setup

all: setup plugin

plugin:
	make -C plugin plugin

test:
	make -C plugin test

image:
	docker build -t komand/go-plugin .
