# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import pytest

from UM.Settings.SettingDefinition import SettingDefinition

benchmark_matches_filter_data = [
    ({ "key": "test" }, True),
    ({ "key": "*est" }, True),
    ({ "default_value": 10 }, True),
    ({ "label": "Test*", "description": "Test*"}, True),
    ({ "minimum_value": 5}, False)
]

@pytest.mark.parametrize("filter,matches", benchmark_matches_filter_data)
def benchmark_matchesFilter(benchmark, filter, matches):
    definition = SettingDefinition("test", None)
    definition.deserialize({
        "label": "Test",
        "type": "int",
        "default_value": 10,
        "description": "Test Setting",
        "children": {
            "test_child_1": {
                "label": "Test Child 1",
                "type": "int",
                "default_value": 20,
                "description": "Test Child Setting 1"
            },
            "test_child_2": {
                "label": "Test Child 2",
                "type": "int",
                "default_value": 20,
                "description": "Test Child Setting 2"
            }
        }
    })

    result = benchmark(definition.matchesFilter, **filter)
    assert result == matches


benchmark_matches_filter_data = [
    ({ "key": "test" }, 1),
    ({ "key": "test*" }, 3),
    ({ "default_value": 10 }, 1),
    ({ "default_value": 20 }, 2),
    ({ "label": "Test*", "description": "Test*"}, 3),
    ({ "minimum_value": 5}, 0),
    ({ "key": "nope"}, 0)
]

@pytest.mark.parametrize("filter,match_count", benchmark_matches_filter_data)
def benchmark_findDefinitions(benchmark, filter, match_count):
    definition = SettingDefinition("test", None)
    definition.deserialize({
        "label": "Test",
        "type": "int",
        "default_value": 10,
        "description": "Test Setting",
        "children": {
            "test_child_1": {
                "label": "Test Child 1",
                "type": "int",
                "default_value": 20,
                "description": "Test Child Setting 1"
            },
            "test_child_2": {
                "label": "Test Child 2",
                "type": "int",
                "default_value": 20,
                "description": "Test Child Setting 2"
            }
        }
    })

    result = benchmark(definition.findDefinitions, **filter)
    assert len(result) == match_count
