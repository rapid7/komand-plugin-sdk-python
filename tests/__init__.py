import unittest
import tests.test_message
import tests.test_action
import tests.test_variables

def komand_test_suite():
    testmodules = [
            test_message,
            test_action,
            test_variables,
            ]

    suite = unittest.TestSuite()

    for t in testmodules:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t.__name__))

    return suite
