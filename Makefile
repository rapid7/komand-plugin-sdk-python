.PHONY: test install build all image

VERSION=$(shell git describe --abbrev=0 --tags)
MAJOR_VERSION=$(shell git describe --abbrev=0 --tags | cut -d"." -f1-2)

MAKE_VERBOSE=0

image:
	docker build -t komand/python-plugin .

all: build test

build:
	python3 setup.py build 

install:
	pip install python_jsonschema_objects==0.3.2
	python3 setup.py install

test:
	python3 setup.py test

tag: image
	@echo version is $(VERSION)
	docker tag komand/python-plugin komand/python-plugin:$(VERSION) 
	docker tag komand/python-plugin:$(VERSION) komand/python-plugin:$(MAJOR_VERSION) 

deploy: tag
	@echo docker login -u "********" -p "********"
	@docker login -u $(KOMAND_DOCKER_USERNAME) -p $(KOMAND_DOCKER_PASSWORD)
	docker push komand/python-plugin:$(VERSION)
	docker push komand/python-plugin:$(MAJOR_VERSION)
