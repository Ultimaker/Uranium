import pytest

from UM.FastConfigParser import FastConfigParser
from UM.Resources import Resources
import configparser  # To compare with the real config parser.
import os
import random  # For the fuzz test. Seeded random so it's still deterministic.

required_headers = [("multi_line", ["general", "values", "metadata"]),
                    ("spacing", ["whatever"]),
                    ("weird_values", ["YAY_omg", "12"])]


setting_values = [("multi_line",    {"values": {
                                        "beep": "omg\nzomg\nbbq",
                                        "zomg": "200",
                                        "foo": "yay\nso\nmuch\ntext to show!",
                                        "short_foo": "some text\nto show"
                                    }, "metadata": {
                                        "oh_noes": "42"
                                    }}),
                  ("spacing",      {"whatever": {
                                        "a": "1",
                                        "b": "2",
                                        "c": "3",
                                        "d": "4",
                                        "e": "5"
                                    }}),
                  ("weird_values", {"YAY_omg": {
                                        "the_value": "[10]",
                                        "more_weirdness": "[]",
                                        "weird_value": "[20,30]",
                                        "even_more_weirdness": "[yay!]",
                                        "woah_weird": "=(200 if the_value != \"whatever\" or more_weirdness == \"derp\" else 0)",
                                        "lesser_equal": "=60 if 1 <= 2 else 30",
                                        "greater_equal": "=20 if 1 >= 2 else \"yay\"",
                                        "key_value_in_string": "G1\n    ; speed_z = {speed_z}\n    speed_something = 20\n    some_other_value = 25\n    speed_y = {speed_z}"
                  }})
                  ]

# Generate fuzz tests.
random.seed(1337)
fuzz_tests = []
elements = "ab= \t\n;%<>\"'"  # Generate keys and values randomly from these elements.
for test_no in range(1000):
    test = "[header]\n"  # Must have at least one header for ConfigParser.
    keys = set()  # Keys must be unique for ConfigParser.
    for key_no in range(6):
        key = ""
        for element_no in range(random.randint(0, 8)):
            key += random.choice(elements)
    for key in keys:
        value = ""
        for element_no in range(random.randint(0, 8)):
            value += random.choice(elements)
        line = "{key}={value}\n".format(key = key, value = value)
        test += line
    fuzz_tests.append(("fuzz" + str(test_no), test))

class TestFastConfigParser:
    config_parser_type = 129
    search_path = os.path.dirname(os.path.abspath(__file__))
    data = {}

    @classmethod
    def readFromFile(cls, file_name):
        path = Resources.getPath(cls.config_parser_type, file_name)
        with open(path, encoding="utf-8") as data:
            return data.read()

    @classmethod
    def setup_class(cls):
        Resources.addType(cls.config_parser_type, "config_parser_files")
        Resources.addSearchPath(cls.search_path)
        cls.data["multi_line"] = cls.readFromFile("multi_line.cfg")
        cls.data["spacing"] = cls.readFromFile("spacing.cfg")
        cls.data["weird_values"] = cls.readFromFile("weird_values.cfg")

    @classmethod
    def teardown_class(cls):
        Resources.removeType(cls.config_parser_type)
        cls.data = {}

    @pytest.mark.parametrize("file_name, header_list", required_headers)
    def test_hasHeaders(self, file_name, header_list):
        parser = FastConfigParser(self.data[file_name])
        for header in header_list:
            assert header in parser

    @pytest.mark.parametrize("file_name, values", setting_values)
    def test_settingValues(self, file_name, values):
        parser = FastConfigParser(self.data[file_name])
        for header_key, setting_pairs in values.items():
            header_data = parser[header_key]
            for key in setting_pairs:
                assert header_data[key] == setting_pairs[key]

    @pytest.mark.parametrize("test_name, contents", fuzz_tests)
    def test_fuzz_configparser(self, test_name, contents):
        """
        Fuzz testing to see if the result is equal to the normal ConfigParser.
        :param test_name: Just an identifier to recognise the test by.
        :param contents: The contents of a hypothetical file.
        """
        parser = FastConfigParser(contents)  # Our own implementation.
        ground_truth = configparser.ConfigParser(interpolation = None)
        ground_truth.read_string(contents)

        # Now see if the result is the same.
        for header in parser:
            assert header in ground_truth
        for header in ground_truth:
            if len(ground_truth[header]) == 0:  # Don't need to also mirror empty headers (ConfigParser always has a "DEFAULT" header).
                continue
            assert header in parser
        for header in parser:
            for key in parser[header]:
                assert key in ground_truth[header]
                assert parser[header][key] == ground_truth[header][key]
            for key in ground_truth[header]:
                assert key in parser[header]
