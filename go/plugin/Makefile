.PHONY: all setup plugin test

export BASE?=$(PWD)/..
export DST?=$(GOPATH)/src/github.com/orcalabs/plugin-sdk


setup:
	test -d $(DST) || ln -s $(BASE) $(DST)

all: setup plugin

plugin:
	cd $(DST)/go/plugin && go get -v ./...
	cd $(DST)/go/plugin && go build .

test:
	cd $(DST)/go/plugin && go test -v ./...
