# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest

from UM.Decorators import interface
from UM.Signal import Signal, signalemitter

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

    def declare_bad_interface():
        @interface
        class TestBadInterface:
            def test(self):
                raise NotImplementedError()

            test_property = "Test"

        return TestBadInterface

    with pytest.raises(TypeError):
        declare_bad_interface()

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
