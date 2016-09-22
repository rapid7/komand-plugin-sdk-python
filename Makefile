.PHONY: test install build all image

VERSION=$(shell git describe --abbrev=0 --tags)
MAJOR_VERSION=$(shell git describe --abbrev=0 --tags | cut -d"." -f1-2)

image:
	docker build -t komand/python-plugin .

all: build test

build:
	python setup.py build 

install:
	python setup.py install

test:
	python setup.py test

tag: image
	@echo version is $(VERSION)
	docker tag komand/python-plugin komand/python-plugin:$(VERSION) 
	docker tag komand/python-plugin:$(VERSION) komand/python-plugin:$(MAJOR_VERSION) 
