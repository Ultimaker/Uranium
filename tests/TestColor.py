import pytest

from UM.Math.Color import Color

half_color = 127/255

test_validate_data = [
    {"data_to_set": [255, 255, 255, 0], "expected": [1.0, 1.0, 1.0, 0.0]},
    {"data_to_set": [0, 0, 0, 255], "expected": [0, 0, 0, 1.0]},
    {"data_to_set": [127, 127, 127, 127], "expected": [half_color, half_color, half_color, half_color]},
    {"data_to_set": [127, 1.0, 127, 127], "expected": [half_color, 1.0, half_color, half_color]}
]

@pytest.mark.parametrize("data", test_validate_data)
def test_getAndSet(data):
    color = Color(*data["data_to_set"])

    assert color == Color(*data["expected"])

    assert color.r == data["expected"][0]
    assert color.g == data["expected"][1]
    assert color.b == data["expected"][2]
    assert color.a == data["expected"][3]

    # And flip the data around to set the values one by one
    reversed_data = data["data_to_set"][::-1]
    color.setR(reversed_data[0])
    color.setG(reversed_data[1])
    color.setB(reversed_data[2])
    color.setA(reversed_data[3])

    assert color.r == data["expected"][3]
    assert color.g == data["expected"][2]
    assert color.b == data["expected"][1]
    assert color.a == data["expected"][0]


hex_data =[
    {"data_to_set": "#FFFFFF", "expected": [1.0, 1.0, 1.0, 1.0]},
    {"data_to_set": "#00000000", "expected": [0.0, 0.0, 0.0, 0.0]},
    {"data_to_set": "#00cc99", "expected": [0 / 255, 204 / 255, 153 / 255, 1.0]},

]

@pytest.mark.parametrize("data", hex_data)
def test_fromHexString(data):
    color = Color.fromHexString(data["data_to_set"])
    expected_color = Color(*data["expected"])
    assert color == expected_color
