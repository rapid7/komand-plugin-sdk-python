.PHONY: all setup plugin test

export BASE?=$(PWD)/..
export DST?=$(GOPATH)/src/github.com/komand/plugin-sdk


setup:
	test -d $(DST) || ln -s $(BASE) $(DST)

all: setup plugin

plugin:
	cd $(DST)/go/plugin && go get -v ./...
	cd $(DST)/go/plugin && go build .

test:
	cd $(DST)/go/plugin && go list ./... | grep -v /vendor/ | go test -v 
