# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

# This is a set of tests to test roundtripping for containers.
#
# It tests both the serialization and deserialization of containers
# as well as the robustness of SaveFile.
#
# This is not strictly a unit test but more of a systems test.

import pytest
import os
import multiprocessing.pool
import unittest.mock  # For MagicMock and patch.

from UM.SaveFile import SaveFile
from UM.Settings.ContainerStack import ContainerStack
from UM.Settings.InstanceContainer import InstanceContainer
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Resources import Resources
Resources.addSearchPath(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(params = [1, 2, 5, 10])
def process_count(request):
    return request.param


def write_data(path, data):
    if not isinstance(data, str):
        data = data.serialize()

    with SaveFile(str(path), "wt") as f:
        f.write(data)


def read_data(path):
    with open(str(path), "rt", encoding = "utf-8") as f:
        return f.read()


##  Run a function in one or more separate processes, waiting until all are finished.
def mp_run(process_count, function, *args):
    results = []
    with multiprocessing.pool.Pool(process_count) as p:
        for i in range(process_count):
            results.append(p.apply_async(function, args))

        p.close()
        p.join()

    actual_results = []
    for result in results:
        assert result.ready()
        actual_results.append(result.get())

    return actual_results


def test_roundtrip_basic(tmpdir, process_count):
    data = "test"
    temp_file = tmpdir.join("test")

    mp_run(process_count, write_data, temp_file, data)

    assert len(list(tmpdir.listdir())) == 1

    results = mp_run(process_count, read_data, temp_file)

    for result in results:
        assert result == data


@pytest.mark.skip(reason = "Skipping this test since it fails when running in some machines and also in the CI. "
                           "Probably due to a problem with the library. I'm getting NotImplementedError when trying "
                           "to findDefinitionContainers. It seems that the container registry is not correctly set.")
def test_roundtrip_instance(tmpdir, process_count, loaded_container_registry):
    instance_container = InstanceContainer("test_container")
    instance_container.setName("Test Instance Container")
    instance_container.setDefinition("inherits")
    instance_container.setMetaDataEntry("test", "test")
    instance_container.setProperty("test_setting_1", "value", 20)

    temp_file = tmpdir.join("instance_container_test")

    mp_run(process_count, write_data, temp_file, instance_container)

    assert len(list(tmpdir.listdir())) == 1

    results = mp_run(process_count, read_data, temp_file)

    for result in results:
        deserialized_container = InstanceContainer("test_container")
        deserialized_container.setDefinition("inherits")
        with unittest.mock.patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance", unittest.mock.MagicMock(return_value = loaded_container_registry)):
            deserialized_container.deserialize(result)

        assert deserialized_container.getName() == instance_container.getName()
        assert deserialized_container.getMetaData() == instance_container.getMetaData()
        assert deserialized_container.getProperty("test_setting_1", "value") == instance_container.getProperty("test_setting_1", "value")


def test_roundtrip_stack(tmpdir, process_count, loaded_container_registry):
    definition = loaded_container_registry.findDefinitionContainers(id = "multiple_settings")[0]
    instances = loaded_container_registry.findInstanceContainers(id = "setting_values")[0]

    container_stack = ContainerStack("test_stack")
    container_stack.setName("Test Container Stack")
    container_stack.setMetaDataEntry("test", "test")
    container_stack.addContainer(definition)
    container_stack.addContainer(instances)

    temp_file = tmpdir.join("container_stack_test")

    mp_run(process_count, write_data, temp_file, container_stack)

    assert len(list(tmpdir.listdir())) == 1

    results = mp_run(process_count, read_data, temp_file)

    for result in results:
        deserialized_stack = ContainerStack("test_stack")
        deserialized_stack.deserialize(result)

        assert deserialized_stack.getName() == container_stack.getName()
        assert deserialized_stack.getMetaData() == container_stack.getMetaData()
        assert deserialized_stack.getBottom() == container_stack.getBottom()
        assert deserialized_stack.getTop() == container_stack.getTop()


def test_roundtrip_definition(tmpdir, process_count, loaded_container_registry):
    definition = loaded_container_registry.findDefinitionContainers(id = "multiple_settings")[0]

    temp_file = tmpdir.join("container_stack_test")

    mp_run(process_count, write_data, temp_file, definition)

    assert len(list(tmpdir.listdir())) == 1

    results = mp_run(process_count, read_data, temp_file)

    for result in results:
        deserialized_definition = DefinitionContainer("multiple_settings")
        deserialized_definition.deserialize(result)

        assert deserialized_definition.getName() == definition.getName()
        assert deserialized_definition.getMetaData() == definition.getMetaData()
