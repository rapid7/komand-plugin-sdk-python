import unittest
from komand import helper
import requests
import os

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

    def test_get_hashes_string_equal_successful(self):
        test_string = "abcdefghijklmnopqrstuvwxyz"
        self.assertDictEqual(
            {"md5": "c3fcd3d76192e4007dfb496cca67e13b",
             "sha1": "32d10c7b8cf96570ca04ce37f2a19d84240d3a89",
             "sha256": "71c480df93d6ae2f1efad1447c66c9525e316218cf51fc8d9ed832f2daf18b73",
             "sha512": "4dbff86cc2ca1bae1e16468a05cb9881c97f1753bce3619034898faa1aabe429955a1bf8ec483d7421fe3c1646613a59ed5441fb0f321389f77f48a879c7b1f1"},
            helper.get_hashes_string(test_string)
        )

    def test_get_hashes_string_not_equal_successful(self):
        test_string = "abcdefghijklmnopqrstuvwxyz"
        self.assertNotEqual(
            {"sha1": "32d10c7b8cf96570ca04ce37f2a19d84240d3a89",
             "sha256": "71c480df93d6ae2f1efad1447c66c9525e316218cf51fc8d9ed832f2daf18b73",
             "sha512": "4dbff86cc2ca1bae1e16468a05cb9881c97f1753bce3619034898faa1aabe429955a1bf8ec483d7421fe3c1646613a59ed5441fb0f321389f77f48a879c7b1f1"},
            helper.get_hashes_string(test_string)
        )

    def test_get_hashes_string_no_exceptions(self):
        test_string = "abcdefghijklmnopqrstuvwxyz"
        try:
            helper.get_hashes_string(test_string)
        except:
            self.fail("Exception was thrown")

    def test_get_hashes_string_all_keys_present(self):
        test_string = "abcdefghijklmnopqrstuvwxyz"
        expected_keys = {"md5", "sha1", "sha256", "sha512"}
        
        hashes = set(helper.get_hashes_string(test_string))
        has_all_keys = len(expected_keys.difference(hashes)) == 0

        self.assertTrue(has_all_keys)

    # check_hashes

    def test_check_hashes_true_md5_success(self):
        test_string = "abcdefghijklmnopqrstuvwxyz"
        self.assertTrue(helper.check_hashes(test_string, "c3fcd3d76192e4007dfb496cca67e13b"))

    def test_check_hashes_false_md5_failure(self):
        test_string = "abcdefghijklmnopqrstuvwxyz"
        self.assertFalse(helper.check_hashes(test_string, "c3fcd3d76192asdfasdfasdf67e13z"))

    def test_check_hashes_true_sha1_success(self):
        test_string = "abcdefghijklmnopqrstuvwxyz"
        self.assertTrue(helper.check_hashes(test_string, "32d10c7b8cf96570ca04ce37f2a19d84240d3a89"))

    def test_check_hashes_false_sha1_failure(self):
        test_string = "abcdefghijklmnopqrstuvwxyz"
        self.assertFalse(helper.check_hashes(test_string, "32d10c7b8cf96570ca04ce37f2a19d84240d3aasdf"))

    def test_check_hashes_true_sha256_success(self):
        test_string = "abcdefghijklmnopqrstuvwxyz"
        self.assertTrue(helper.check_hashes(test_string, "71c480df93d6ae2f1efad1447c66c9525e316218cf51fc8d9ed832f2daf18b73"))

    def test_check_hashes_false_sha256_failure(self):
        test_string = "abcdefghijklmnopqrstuvwxyz"
        self.assertFalse(helper.check_hashes(test_string, "71c480df93d6ae2f1efad1447c66c9525e316218cf51fc8d9ed832f2dafasdfasdf"))

    def test_check_hashes_true_sha512_success(self):
        test_string = "abcdefghijklmnopqrstuvwxyz"
        self.assertTrue(helper.check_hashes(test_string,
                                            "4dbff86cc2ca1bae1e16468a05cb9881c97f1753bce3619034898faa1aabe429955a1bf8ec483d7421fe3c1646613a59ed5441fb0f321389f77f48a879c7b1f1"))

    def test_check_hashes_false_sha512_failure(self):
        test_string = "abcdefghijklmnopqrstuvwxyz"
        self.assertFalse(helper.check_hashes(test_string,
                                             "4dbff86cc2ca1bae1e16468a05cb9881c97f1753bce3619034898faa1aabe429955a1bf8ec483d7421fe3c1646613a59ed5441fb0f32138asdfasdf"))

    # open_url

    # We can't reliably test known responses against dynamic responses from an endpoint we don't control,
    # so this is the best we can do (to verify Python 2/3 compatibility
    def test_open_url_no_exceptions(self):
        try:
            response = helper.open_url(url="https://api.ipify.org?format=json")
            self.assertIsNotNone(response)
        except:
            self.fail("Exception caught")

    # check_url

    def test_check_url_success(self):
        self.assertTrue(helper.check_url("https://google.com"))

    def test_check_url_exception(self):
        with self.assertRaises(requests.exceptions.InvalidURL):
            helper.check_url("http:google.com")

    # exec_command

    def test_exec_command_success(self):
        result = helper.exec_command("ls")
        expected_keys = {"stdout", "rcode", "stderr"}
        set_diff = expected_keys.difference(set(result))
        has_keys = len(set_diff) == 0
        self.assertTrue(has_keys)

    # encode_string

    def test_encode_string(self):
        sample = "hello world"
        expected = b'aGVsbG8gd29ybGQ='

        encoded = helper.encode_string(sample)

        self.assertEqual(expected, encoded)

    def test_encode_file_success(self):
        expected = "a29tYW5kIGlzIGF3ZXNvbWU="

        f = open("test.txt", "w+")
        f.write("komand is awesome")
        f.close()

        actual = helper.encode_file("./test.txt")
        self.assertEqual(expected, actual)

        os.remove("test.txt")

    # check_url_modified

    def test_check_url_modified_false(self):
        self.assertFalse(helper.check_url_modified("https://httpstat.us/304"))

    def test_check_url_modified_true(self):
        self.assertTrue(helper.check_url_modified("https://httpstat.us/200"))

    # get_url_content_disposition

    def test_get_url_content_disposition_success(self):
        headers = {"Content-Type": "text/html; charset=utf-8",
                    "Content-Disposition": "attachment; filename=test.html",
                    "Content-Length": 22
        }

        self.assertEqual("test.html", helper.get_url_content_disposition(headers))

    # get_url_path_filename

    def test_get_url_path_filename_success(self):
        sample = "https://dl.google.com/chrome/mac/stable/GGRO/googlechrome.dmg"
        expected = "googlechrome.dmg"

        self.assertEqual(expected, helper.get_url_path_filename(sample))

    def test_get_url_path_filename_success_with_two_periods(self):
        sample = "https://dl.google.com/chrome/mac/stable/GGRO/google.chrome.dmg"
        expected = "google.chrome.dmg"

        self.assertEqual(expected, helper.get_url_path_filename(sample))

    # get_url_filename

    def test_get_url_filename_successful(self):
        expected = "googlechrome.dmg"
        self.assertEqual(expected, helper.get_url_filename("https://dl.google.com/chrome/mac/stable/GGRO/googlechrome.dmg"))

