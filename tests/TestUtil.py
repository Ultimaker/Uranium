from unittest.mock import MagicMock

from UM.Util import parseBool
import pytest

positive_results = [True, "True", "true", "Yes", "yes", 1]
negative_results = [False, "False", "false", "No", "no", 0, None, "I like turtles", MagicMock()]


@pytest.mark.parametrize("value", positive_results)
def test_positive(value):
    assert parseBool(value)


@pytest.mark.parametrize("value", negative_results)
def test_negative(value):
    assert not parseBool(value)