.PHONY: test install build all

all: build test

build:
	python setup.py build 

install:
	python setup.py install

test:
	python setup.py test

image:
	docker build -t komand/python-plugin .
