SHELL := /bin/bash

.PHONY: test install build all image

VERSION=$(shell git describe --abbrev=0 --tags)
MAJOR_VERSION=$(shell echo $(VERSION) | cut -d"." -f1)
MINOR_VERSION=$(shell echo $(VERSION) | cut -d"." -f1-2)

PYTHON_VERSION=$(shell python --version 2>&1 | cut -d ' ' -f 2)
PYTHON_MAJOR_VERSION=$(shell echo $(PYTHON_VERSION) | cut -d"." -f1)

# Default to Python 3
DOCKERFILE=3-38

MAKE_VERBOSE=0

build-image:
	docker build -t rapid7/insightconnect-python-$(DOCKERFILE)-plugin -f dockerfiles/$(DOCKERFILE) .
	docker tag rapid7/insightconnect-python-${DOCKERFILE}-plugin rapid7/insightconnect-python-${DOCKERFILE}-plugin:$(VERSION)
	docker tag rapid7/insightconnect-python-${DOCKERFILE}-plugin rapid7/insightconnect-python-${DOCKERFILE}-plugin:$(MINOR_VERSION)
	docker tag rapid7/insightconnect-python-${DOCKERFILE}-plugin rapid7/insightconnect-python-${DOCKERFILE}-plugin:$(MAJOR_VERSION)

all: test tag

install:
	python setup.py build

test:
	pip install tox
	tox

deploy-image: build-image
	@echo docker login -u "********" -p "********"
	@docker login -u $(KOMAND_DOCKER_USERNAME) -p $(KOMAND_DOCKER_PASSWORD)

	docker push rapid7/insightconnect-python-${DOCKERFILE}-plugin
	docker push rapid7/insightconnect-python-${DOCKERFILE}-plugin:$(VERSION)
	docker push rapid7/insightconnect-python-${DOCKERFILE}-plugin:$(MINOR_VERSION)
	docker push rapid7/insightconnect-python-${DOCKERFILE}-plugin:$(MAJOR_VERSION)

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

run-sample:
	# Exit early if sample doesn't exist
	if [ ! -d "samples/$(sample)" ]; then \
		echo "ERROR: $(sample) sample plugin doesn't exist; confirm spelling or existence and try again" && exit 1; \
	fi
	# Build and install plugin sdk library
	python setup.py build && python setup.py install
	# Build and install plugin
	cd samples/$(sample) ; python setup.py build && python setup.py install
	# Run plugin in http mode
	cd samples/$(sample) ; ./bin/icon_$(sample) http
