.PHONY: all

export BASE?=$(PWD)/..
export DST?=$(GOPATH)/src/github.com/orcalabs/plugin-sdk

all:
	test -d $(DST) || ln -s $(BASE) $(DST)

	cd $(DST)/go && go get -v ./...
	cd $(DST)/go && go build .
