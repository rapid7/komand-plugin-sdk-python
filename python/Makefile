.PHONY: test install build all

all: build test

build:
	python setup.py build 

install:
	python setup.py install

test:
	python setup.py test

docker_build:
	docker build -t komand-plugin-python .
