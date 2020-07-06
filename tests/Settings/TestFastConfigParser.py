import pytest

from UM.FastConfigParser import FastConfigParser
from UM.Resources import Resources
import os

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
                                        "woah_weird": "=(200 if the_value != \"whatever\" or more_weirdness == \"derp\" else 0)"
                  }})
                  ]


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