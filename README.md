
# Komand Python SDK [![Build Status](https://travis-ci.org/rapid7/komand-plugin-sdk-python.svg?branch=master)](https://travis-ci.org/rapid7/komand-plugin-sdk-python)

The Komand Python SDK is used for building plugins in Python for
Rapid7 InsightConnect (previously Komand).

[Documentation](https://komand.github.io/python/start.html)

## Changelog

* 3.3.0 - Add webserver route to allow for threading changes

* 3.2.0 - Add new ConnectionTestException/PluginException presets:
 UNKNOWN, BASE64_ENCODE, BASE64_DECODE, INVALID_JSON |
 Add an optional data parameter for formatting response output