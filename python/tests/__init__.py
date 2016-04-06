import unittest
import test_message
import test_action

def komand_test_suite():
    testmodules = [
            test_message,
            test_action,
            ]

    suite = unittest.TestSuite()

    for t in testmodules:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t.__name__))

    return suite
