SHELL := /bin/bash

.PHONY: test install build all image

VERSION=$(shell git describe --abbrev=0 --tags)
MAJOR_VERSION=$(shell echo $(VERSION) | cut -d"." -f1)
MINOR_VERSION=$(shell echo $(VERSION) | cut -d"." -f1-2)

PYTHON_VERSION=$(shell python --version 2>&1 | cut -d ' ' -f 2)
PYTHON_MAJOR_VERSION=$(shell echo $(PYTHON_VERSION) | cut -d"." -f1)

ifndef TRAVIS_PYTHON_VERSION
TRAVIS_PYTHON_VERSION=$(shell echo $(PYTHON_MAJOR_VERSION))
endif

DOCKERFILE=$(shell echo $(TRAVIS_PYTHON_VERSION) | cut -d"." -f1)

MAKE_VERBOSE=0

image:
	# Build all 2/3-slim Docker images
	@for dockerfile in $(wildcard dockerfiles/${DOCKERFILE}*); do \
		F=$${dockerfile//dockerfiles\/}; \
		docker build -t komand/python-$${F}-plugin -f dockerfiles/$${F} .; \
	done

all: test tag

build:
	python setup.py build

install:
	python setup.py install

test:
	tox

tag: image
	@echo version is $(VERSION)

	# Tag all 2/3-slim Docker images
	@for dockerfile in $(wildcard dockerfiles/${DOCKERFILE}*); do \
		F=$${dockerfile//dockerfiles\/}; \
		docker tag komand/python-$${F}-plugin komand/python-$${F}-plugin:$(VERSION); \
		docker tag komand/python-$${F}-plugin komand/python-$${F}-plugin:$(MINOR_VERSION); \
		docker tag komand/python-$${F}-plugin komand/python-$${F}-plugin:$(MAJOR_VERSION); \
	done

deploy: tag
	@echo docker login -u "********" -p "********"
	@docker login -u $(KOMAND_DOCKER_USERNAME) -p $(KOMAND_DOCKER_PASSWORD)

	# Deploy all 2/3-slim Docker images
	@for dockerfile in $(wildcard dockerfiles/${DOCKERFILE}*); do \
		F=$${dockerfile//dockerfiles\/}; \
		docker push komand/python-$${F}-plugin; \
		docker push komand/python-$${F}-plugin:$(VERSION); \
		docker push komand/python-$${F}-plugin:$(MINOR_VERSION); \
		docker push komand/python-$${F}-plugin:$(MAJOR_VERSION); \
	done

# Release targets for PyPi
packagedeps:
	python3 -m pip install --user --upgrade setuptools wheel twine

package:
	rm -rf dist/
	python3 setup.py sdist bdist_wheel

disttest: package
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

distprod: package
	python3 -m twine upload dist/*
