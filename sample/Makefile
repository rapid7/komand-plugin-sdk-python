NAME?=foobar
VENDOR?=komand
VERSION?=0.1.0
PKG=$(VENDOR)-$(NAME)-$(VERSION).tar.gz 

DST?=/komand/plugins/bin

all: image

plugin: build package 

build:
	python setup.py install	

package:
	rm -rf $(PKG)
	tar -cvzf $(PKG) --exclude=$(PKG) *

image:
	docker build --no-cache -t $(VENDOR)/$(NAME):$(VERSION) .
	docker tag -f $(VENDOR)/$(NAME):$(VERSION) $(VENDOR)/$(NAME):latest

.PHONY: all package image build plugin
