import unittest
import tests.test_message
import tests.test_action
import tests.test_variables
import tests.test_custom_encoder
# import tests.test_helpers

def komand_test_suite():
    testmodules = [
        test_message,
        test_action,
        test_variables,
        test_custom_encoder
        ]

    suite = unittest.TestSuite()

    for t in testmodules:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t.__name__))

    return suite
