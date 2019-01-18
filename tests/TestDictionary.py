import pytest
import UM.Dictionary


def test_findKey():
    test_dict = {"omg": "zomg", "beep": "meep"}
    assert UM.Dictionary.findKey(test_dict, "zomg") == "omg"
    assert UM.Dictionary.findKey(test_dict, "meep") == "beep"

    with pytest.raises(ValueError):
        UM.Dictionary.findKey(test_dict, "Nope")
