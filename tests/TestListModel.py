from unittest import TestCase

from PyQt5.QtCore import Qt, QModelIndex

from UM.Qt.ListModel import ListModel
from copy import deepcopy

class TestListModel(TestCase):

    list_model = None  # type: ListModel

    test_data = [{"name": "yay", "data": 12}, {"name": "omg", "data": 13}, {"name":"zomg", "data": 14}]
    NameRole = Qt.UserRole + 1
    DataRole = Qt.UserRole + 2

    def setUp(self):
        self.list_model = ListModel()
        self.list_model.addRoleName(self.NameRole, "name")
        self.list_model.addRoleName(self.DataRole, "data")

        self.list_model.setItems(deepcopy(self.test_data))

    def test_getItem(self):
        assert self.list_model.getItem(0) == {"name": "yay", "data": 12}
        assert self.list_model.getItem(9001) == {}

    def test_items(self):
        assert self.list_model.items == self.test_data

    def test_insertItem(self):
        self.list_model.insertItem(0, {"name": "zomg!", "data": "yay"})
        assert self.list_model.getItem(0) == {"name": "zomg!", "data": "yay"}
        # Check if the previously first item is now the second one.
        assert self.list_model.getItem(1) == {"name": "yay", "data": 12}

    def test_removeItem(self):
        self.list_model.removeItem(1)
        assert self.list_model.getItem(1) == {"name":"zomg", "data": 14}

    def test_clear(self):
        assert self.list_model.count == 3
        self.list_model.clear()
        assert self.list_model.count == 0

    def test_appendItem(self):
        self.list_model.appendItem({"name":"!", "data": 9001})
        assert self.list_model.count == 4
        assert self.list_model.getItem(3) == {"name":"!", "data": 9001}

    def test_setProperty(self):
        self.list_model.setProperty(0, "name", "new_data")
        assert self.list_model.getItem(0)["name"] == "new_data"

    def test_find(self):
        assert self.list_model.find("name", "omg") == 1
        assert self.list_model.find("data", 13) == 1
        assert self.list_model.find("name", "zomg") == 2

        assert self.list_model.find("name", "UNKNOWN") == -1

    def test_setItems(self):
        self.list_model.setItems([{"name": "zomg!", "data": "yay"}])
        assert self.list_model.items == [{"name": "zomg!", "data": "yay"}]

    def test_sort(self):
        self.list_model.sort(lambda i: -i["data"])

        assert self.list_model.getItem(0) == {"name":"zomg", "data": 14}
        assert self.list_model.getItem(2) == {"name": "yay", "data": 12}