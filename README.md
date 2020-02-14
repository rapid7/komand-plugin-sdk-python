
# Komand Python SDK [![Build Status](https://travis-ci.org/rapid7/komand-plugin-sdk-python.svg?branch=master)](https://travis-ci.org/rapid7/komand-plugin-sdk-python)

The Komand Python SDK is used for building plugins in Python for Rapid7 InsightConnect (previously Komand). The project
is currently built by [Travis CI](https://travis-ci.org/rapid7/komand-plugin-sdk-python) and results in base Docker 
images used as the runtimes for InsightConnect plugins.

Docker images created during the build and deployment of the Python SDK are uploaded to the [Komand repositories on 
Dockerhub](https://hub.docker.com/u/komand/).

Further [documentation](https://komand.github.io/python/start.html) for building an InsightConnect plugin is available to get started.

## Development of the Python SDK

You will need to have some or all of the following dependencies installed, depending on what you're doing while building 
or testing the Python SDK:

- Python 3
- Python 2
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

## Changelog

* X.X.X - Add development details to README |
 Add run-local makefile rule for ease of development

* 3.2.0 - Add new ConnectionTestException/PluginException presets:
 UNKNOWN, BASE64_ENCODE, BASE64_DECODE, INVALID_JSON |
 Add an optional data parameter for formatting response output