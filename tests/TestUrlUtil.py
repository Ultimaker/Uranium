# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
import re
from unittest import TestCase
from unittest.mock import patch
from urllib.parse import urlparse

from UM.Qt.Bindings.Utilities import UrlUtil

from io import StringIO


class TestUrlUtil(TestCase):

    def setUp(self) -> None:
        self.url_util = UrlUtil()

    def test_urlHasValidScheme_url_scheme_valid_and_in_allowed_schemes(self):
        """
        Tests the happy scenario. When the scheme of the url is a valid scheme (http or https) and it is
        in the allowed schemes.

        :return: None
        """
        self.assertTrue(self.url_util._urlHasValidScheme("https://www.ultimaker.com", ["https"]))
        self.assertTrue(self.url_util._urlHasValidScheme("http://www.angusj.com/delphi/clipper.php", ["http"]))
        self.assertTrue(self.url_util._urlHasValidScheme("http://www.angusj.com/delphi/clipper.php", ["http", "https"]))

    def test_urlHasValidScheme_allowed_invalid_scheme_generates_warning(self):
        """
        Tests the following unhappy scenario:
        If we try to allow an invalid scheme when calling the function (anything other than http or https), then a
        warning message that mentions all the invalid schemes should be generated in the console.
        This warning message lets the developer know that he/she is trying to allow an invalid scheme.

        :return: None
        """
        invalid_schemes = [["mailto"], ["ftp"], ["blue", "potato"]]
        for schemes_list in invalid_schemes:
            with patch('sys.stdout', new=StringIO()) as mock_output:  # re-routes the output inside mock_output
                allowed_schemes = ["https"]
                allowed_schemes.extend(schemes_list)
                self.url_util._urlHasValidScheme("https://www.ultimaker.com", allowed_schemes)

                # Ensure the correct message is outputted in the console
                expected_output = re.sub(r'\W+', ' ', "Attempted to allow invalid schemes")  # remove special characters
                console_ouput = re.sub(r'\W+', ' ', mock_output.getvalue().strip())
                self.assertIn(expected_output, console_ouput)  # Assert the correct message is in the console output
                for scheme in schemes_list:
                    self.assertIn(scheme, console_ouput)  # Assert each of the schemes that are being tested appears in the console output

    def test_urlHasValidScheme_url_scheme_not_in_allowed_schemes(self):
        """
        Tests the following unhappy scenario:
        If the function tries to open a URL with a scheme that is not allowed, the function should generate an error
        message indicating that the url has a disallowed scheme.

        :return:
        """
        invalid_combinations = (("https://www.ultimaker.com", ["http"]), ("http://www.ultimaker.com", ["https"]))
        for url, allowed_schemes in invalid_combinations:
            with patch('sys.stdout', new=StringIO()) as mock_output:  # re-routes the output inside mock_output

                # Ensure the function fails
                self.assertFalse(self.url_util._urlHasValidScheme(url, allowed_schemes))

                # Ensure the correct message is outputted in the console
                expected_output = "The scheme '{scheme}' is not in the allowed schemes".format(scheme = urlparse(url).scheme)
                expected_output = re.sub(r'\W+', ' ', expected_output)  # remove special characters
                console_ouput = mock_output.getvalue().strip()
                console_ouput = re.sub(r'\W+', ' ', console_ouput)  # remove special characters
                self.assertIn(expected_output, console_ouput)
                for scheme in allowed_schemes:
                    self.assertIn(scheme, console_ouput)

