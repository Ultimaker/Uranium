# Copyright (c) 2024 UltiMaker
# Uranium is released under the terms of the LGPLv3 or higher.
from unittest.mock import MagicMock

import pytest

from UM.Decorators import interface, CachedMemberFunctions, cache_per_instance, cache_per_instance_copy_result

def test_interface():
    def declare_interface():
        @interface
        class TestInterface:
            def test(self):
                pass

            def test2(self):
                pass

        return TestInterface

    cls = declare_interface()
    assert cls is not None

    def declare_subclass(cls):
        class TestSubclass(cls):
            def __init__(self):
                super().__init__()

            def test(self):
                print("test")

            def test2(self):
                print("test2")

        return TestSubclass

    cls = declare_subclass(cls)
    assert cls is not None

    sub = cls()
    assert sub is not None

    def declare_bad_subclass():
        @interface
        class TestInterface:
            def test(self):
                pass

        class TestSubclass(TestInterface):
            pass

        return TestSubclass()

    with pytest.raises(NotImplementedError):
        declare_bad_subclass()

    def declare_good_signature():
        @interface
        class TestInterface:
            def test(self, one, two, three = None):
                pass

        class TestSubclass(TestInterface):
            def test(self, one, two, three = None):
                pass

        return TestSubclass()

    sub = declare_good_signature()
    assert sub is not None

    def declare_bad_signature():
        @interface
        class TestInterface:
            def test(self, one, two, three = None):
                pass

        class TestSubclass(TestInterface):
            def test(self, one):
                pass

        return TestSubclass()

    with pytest.raises(NotImplementedError):
        declare_bad_signature()

    #
    # private functions should be ignored
    #
    def should_ignore_private_functions():
        @interface
        class TestInterface:
            def __should_be_ignored(self):
                pass

        class TestSubClass(TestInterface):
            pass

        return TestSubClass()

    sub = should_ignore_private_functions()
    assert sub is not None


def test_cachePerInstance():

    CachedMemberFunctions._CachedMemberFunctions__cache = {}
    bigDeal = MagicMock()

    class SomeClass:
        def __init__(self):
            self._map = {}

        @cache_per_instance
        def getThing(self, a):
            bigDeal()
            return self._map.get(a, None)

        @cache_per_instance_copy_result
        def getList(self):
            bigDeal()
            return [234, 456, 789]

        def setThing(self, a, b):
            CachedMemberFunctions.clearInstanceCache(self)
            self._map[a] = b

    instance = SomeClass()

    instance.setThing("marco", "polo")
    instance.getThing("marco")
    instance.getThing("marco")
    assert instance.getThing("marco") == "polo"
    assert bigDeal.call_count == 1

    instance.setThing("marco", "bolo")
    assert instance.getThing("marco") == "bolo"
    assert bigDeal.call_count == 2
    instance.getThing("marco")
    instance.getThing("marco")
    assert bigDeal.call_count == 2

    other = SomeClass()
    other.setThing("marco", "yolo")
    other.getThing("marco")
    other.getThing("marco")
    assert other.getThing("marco") == "yolo"
    assert bigDeal.call_count == 3

    assert len(CachedMemberFunctions._CachedMemberFunctions__cache) == 2
    CachedMemberFunctions.deleteInstanceCache(instance)
    assert len(CachedMemberFunctions._CachedMemberFunctions__cache) == 1

    lizt = other.getList()
    assert lizt == [234, 456, 789]
    lizt.append(111)
    assert other.getList() == [234, 456, 789]
