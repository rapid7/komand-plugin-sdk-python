.PHONY: test install build all

image:
	docker build -t komand/python-plugin .

all: build test

build:
	python setup.py build 

install:
	python setup.py install

test:
	python setup.py test

