import unittest
from komand import helper


class TestHelpers(unittest.TestCase):

    # extract_value

    def test_extract_value_successful(self):
        result = helper.extract_value(r'\s', 'Shell', r':\s(.*)\s', '\nShell: /bin/bash\n')
        self.assertEqual("/bin/bash", result)

    def test_extract_value_failure(self):
        result = helper.extract_value(r'\s', 'Shell', r':\s(.*)\s', '\nShell: /bin/bash\n')
        self.assertNotEqual("/bin/bas", result)

    def test_extract_no_exceptions(self):
        try:
            helper.extract_value(r'\s', 'Shell', r':\s(.*)\s', '\nShell: /bin/bash\n')
        except:
            self.fail("Exception was thrown")

    # clean_dict

    def test_clean_dict_not_equal_successful(self):
        sample = {"one": None, "two": "", "three": "woohoo"}
        self.assertNotEqual(sample, helper.clean_dict({"one": None, "two": "", "three": "woohoo"}))

    def test_clean_dict_equal_successful(self):
        sample = {"three": "woohoo"}
        self.assertDictEqual(sample, helper.clean_dict({"one": None, "two": "", "three": "woohoo"}))

    def test_clean_dict_no_exceptions(self):
        try:
            helper.clean_dict({"test": "yay"})
        except:
            self.fail("Exception was thrown")

    # clean_list

    def test_clean_list_not_equal_successful(self):
        sample = ["", None, "test"]
        self.assertNotEqual(sample, helper.clean_list(["", None, "test"]))

    def test_clean_list_equal_successful(self):
        sample = ["test"]
        self.assertEqual(sample, helper.clean_list(["", None, "test"]))

    def test_clean_list_no_exceptions(self):
        try:
            helper.clean_list([])
        except:
            self.fail("Exception was thrown")

    # clean

    def test_clean_not_equal_list_successful(self):
        sample = ["one", {"two": "", "three": None}, {"four": 4}, None]
        self.assertNotEqual(sample, helper.clean(["one", {"two": "", "three": None}, {"four": 4}, None]))

    def test_clean_equal_list_successful(self):
        sample = ["one", {"two": "", "three": None}, {"four": 4}, None]
        self.assertEqual(["one", {}, {"four": 4}], helper.clean(sample))

    def test_clean_not_equal_dict_successful(self):
        sample = {"one": [1, None, "", {"two": None}, {"three": 3}], "four": 4}
        self.assertNotEqual(sample, helper.clean({"one": [1, None, "", {"two": None}, {"three": 3}], "four": 4}))

    def test_clean_equal_dict_successful(self):
        sample = {"one": [1, None, "", {"two": None}, {"three": 3}], "four": 4}
        self.assertEqual({"one": [1, {}, {"three": 3}], "four": 4}, helper.clean(sample))

    def test_clean_no_exceptions(self):
        try:
            helper.clean({"one": [1, None, "", {"two": None}, {"three": 3}], "four": 4})
        except:
            self.fail("Exception was thrown")

    # get_hashes_string

    def test_get_hashes_string(self):
        test_string = "abcdefghijklmnopqrstuvwxyz"
        self.assertDictEqual(
            {"md5": "c3fcd3d76192e4007dfb496cca67e13b",
             "sha1": "32d10c7b8cf96570ca04ce37f2a19d84240d3a89",
             "sha256": "71c480df93d6ae2f1efad1447c66c9525e316218cf51fc8d9ed832f2daf18b73",
             "sha512": "4dbff86cc2ca1bae1e16468a05cb9881c97f1753bce3619034898faa1aabe429955a1bf8ec483d7421fe3c1646613a59ed5441fb0f321389f77f48a879c7b1f1"},
            helper.get_hashes_string(test_string)
        )