
# Komand Python SDK [![Build Status](https://travis-ci.org/rapid7/komand-plugin-sdk-python.svg?branch=master)](https://travis-ci.org/rapid7/komand-plugin-sdk-python)

The Komand Python SDK is used for building plugins in Python for Rapid7 InsightConnect (previously Komand). The project
is currently built by [Travis CI](https://travis-ci.org/rapid7/komand-plugin-sdk-python) and results in base Docker 
images used as the runtimes for InsightConnect plugins.

Docker images created during the build and deployment of the Python SDK are uploaded to the [Komand Docker Repositories](https://hub.docker.com/u/komand/).

Further [documentation](https://komand.github.io/python/start.html) for building an InsightConnect plugin is available to get started.

## Development of the Python SDK

The Python SDK codebase is built to support Python 3.8+ as of version 4.0.0. Prior [SDK releases](https://github.com/rapid7/komand-plugin-sdk-python/releases) 
will need to be referenced for any Python 2.7 or 3.7 needs. 

You will need to have the following dependencies installed when developing or testing the Python SDK:

- Python 3.8
- Docker
- make
- tox

### Building and Installing the SDK

To build and install the SDK locally, first created a Python virtual environment for the particular Python version and
activate it. Then build, install, and confirm the package has been installed.
```
> python3 -m venv venv
> source venv/bin/activate
> python setup.py build
> python setup.py install
> pip list | grep komand
komand                    3.2.0
```

### Testing Sample Plugin
The easiest way to test changes to the SDK is by running it locally against one of the [sample plugins](./samples) 
included in the repository. Make sure a virtual environment has been activated and then pass in the sample directory 
name as a parameter:
```
> make sample=example run-sample
```

Once the SDK and plugin python packages have been built and installed, the plugin will be started in `http` mode and 
listening at `http:0.0.0.0:10001`:
```
[2020-02-13 23:21:13 -0500] [56567] [INFO] Starting gunicorn 19.7.1
[2020-02-13 23:21:13 -0500] [56567] [INFO] Listening at: http://0.0.0.0:10001 (56567)
[2020-02-13 23:21:13 -0500] [56567] [INFO] Using worker: threads
[2020-02-13 23:21:13 -0500] [56571] [INFO] Booting worker with pid: 56571
```

To build, install, and run SDK changes without the use of the `run-sample` rule, the below steps can be used:
```
> python setup.py build && python setup.py install
> cd samples/example
> python setup.py build && python setup.py install
> ./bin/icon_example http
```

### Testing Locally with Image

In addition to testing the SDK and resulting plugin python package, it is also possible to build a plugin locally and 
test it as it would be used by the InsightConnect orchestrator.

TODO: This needs updates to makefile to build single docker image
```
> cd samples/example
> icon-plugin build image --no-pull
> docker run -it -p 10001:10001 rapid7/example:latest http
```

## Running Tests

In order to run tests for the Python SDK, first ensure `tox` has been installed. Tox makes it easy for testing this 
project in isolated virtual environments and for specific Python versions. To install tox:
```
> pip install tox
```

Running all tests:
```
> tox
```

Running a specific test file:
```
> tox -e py38 -- tests/plugin/hello_world/tests/test_cli.py
```

## Release

To release a new version of the Python SDK, the below steps must be followed:

1. Create a Pull Request with your changes to be merged into master
2. Merge changes after receiving at least one approval
3. Create a versioned tag off of release; version must follow SemVer
4. [Travis CI](https://travis-ci.org/rapid7/komand-plugin-sdk-python) will perform a matrix build and release based on the recently created tag

Travis utilizes a build matrix located in the [.travis.yml](.travis.yml) file located within the SDK to build with the 
desired Python versions and then push them to their respective repositories.

## Changelog

* 4.0.0 - Add API, plugin spec, plugin info, list actions/triggers and status routes | Add docstrings for existing routes | End support for Python2 and PyPy | Add development details to README |
 Add run-local makefile rule for ease of development
* 3.3.0 - Add webserver route to allow for threading changes
* 3.2.0 - Add new ConnectionTestException/PluginException presets:
 UNKNOWN, BASE64_ENCODE, BASE64_DECODE, INVALID_JSON |
 Add an optional data parameter for formatting response output