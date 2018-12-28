# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import pytest

from UM.Settings.ContainerQuery import ContainerQuery


def test_matchMultipleTokens():
    cq = ContainerQuery(None)

    # Test #1: if property_name doesn't exist, it will return False
    result = cq._matchRegMultipleTokens({"name": "test"}, "type", "123")
    assert result is False

    test_cases = [
        {"input": {"metadata": {"name": "test"},  # Single token, match
                   "property_name": "name",
                   "value": "[test]",
                   },
         "match": True,
         },
        {"input": {"metadata": {"name": "test1"},  # Single token, no match
                   "property_name": "name",
                   "value": "[test]",
                   },
         "match": False,
         },
        {"input": {"metadata": {"name": "test"},  # Multiple token, match
                   "property_name": "name",
                   "value": "[abc|123|test|456]",
                   },
         "match": True,
         },
        {"input": {"metadata": {"name": "test"},  # Multiple token, no match
                   "property_name": "name",
                   "value": "[abc|_test_|test2|tst]",
                   },
         "match": False,
         },
    ]

    for test_case in test_cases:
        result = cq._matchRegMultipleTokens(**test_case["input"])
        if test_case["match"]:
            assert result is not None
        else:
            assert result is None
