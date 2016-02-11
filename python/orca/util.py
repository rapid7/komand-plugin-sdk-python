import sys

def trace(exception):
    """Returns the trace from an exception"""
    return sys.exc_info()[2]

