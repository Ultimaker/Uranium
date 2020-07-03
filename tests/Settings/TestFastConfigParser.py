import pytest

from UM.FastConfigParser import FastConfigParser
from UM.Resources import Resources
import os

required_headers = [("multi_line", ["general", "values", "metadata"])]


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

    @classmethod
    def teardown_class(cls):
        Resources.removeType(cls.config_parser_type)
        cls.data = {}

    @pytest.mark.parametrize("file_name, header_list", required_headers)
    def test_hasHeaders(self, file_name, header_list):
        parser = FastConfigParser(self.data[file_name])
        for header in header_list:
            assert header in parser