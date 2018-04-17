.PHONY: test install build all image

VERSION=$(shell git describe --abbrev=0 --tags)
MAJOR_VERSION=$(shell echo $(VERSION) | cut -d"." -f1)
MINOR_VERSION=$(shell echo $(VERSION) | cut -d"." -f1-2)

PYTHON_VERSION=$(shell python --version 2>&1 | cut -d ' ' -f 2)
PYTHON_MAJOR_VERSION=$(shell echo $(PYTHON_VERSION) | cut -d"." -f1)

ifndef DOCKERFILE_SUFFIX
DOCKERFILE_SUFFIX=$(shell echo python-$(PYTHON_MAJOR_VERSION))
endif

MAKE_VERBOSE=0

image:
	docker build -t komand/python-$(PYTHON_MAJOR_VERSION)-plugin -f Dockerfile-python$(PYTHON_MAJOR_VERSION) .

python-2-image:
	docker build -t komand/python-2-plugin:test -f Dockerfile-python2 .

python-3-image:
	docker build -t komand/python-3-plugin:test -f Dockerfile-python3 .

all: test tag

build:
	python setup.py build

install:
	python setup.py install

test:
	tox

tag: image
	@echo version is $(VERSION)
	docker tag komand/python-$(PYTHON_MAJOR_VERSION)-plugin komand/python-$(PYTHON_MAJOR_VERSION)-plugin:$(VERSION)
	docker tag komand/python-$(PYTHON_MAJOR_VERSION)-plugin komand/python-$(PYTHON_MAJOR_VERSION)-plugin:$(MINOR_VERSION)
	docker tag komand/python-$(PYTHON_MAJOR_VERSION)-plugin komand/python-$(PYTHON_MAJOR_VERSION)-plugin:$(MAJOR_VERSION)

deploy: tag
	@echo docker login -u "********" -p "********"
	@docker login -u $(KOMAND_DOCKER_USERNAME) -p $(KOMAND_DOCKER_PASSWORD)
	docker push komand/python-$(PYTHON_MAJOR_VERSION)-plugin
	docker push komand/python-$(PYTHON_MAJOR_VERSION)-plugin:$(VERSION)
	docker push komand/python-$(PYTHON_MAJOR_VERSION)-plugin:$(MINOR_VERSION)
	docker push komand/python-$(PYTHON_MAJOR_VERSION)-plugin:$(MAJOR_VERSION)
