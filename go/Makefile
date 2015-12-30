.PHONY: all

export BASE?=$(PWD)/..
export DST?=$(GOPATH)/src/github.com/orcalabs/plugin-sdk


setup:
	test -d $(DST) || ln -s $(BASE) $(DST)

all: setup
	cd $(DST)/go && go get -v ./...
	cd $(DST)/go && go build .

test:
	cd $(DST)/go && go test -v ./...
