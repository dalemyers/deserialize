"""Test downcasting."""

import copy
import os
import sys
from typing import List
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position

# pylint: disable=blacklisted-name


class SomeRandomBase:
    """A sample base class."""

    hello: str


@deserialize.downcast_field("type_name")
class DowncastableBase:
    """A downcastable base class."""

    type_name: str


@deserialize.downcast_identifier(DowncastableBase, "foo")
class Foo(DowncastableBase):
    """Downcastable class."""

    one: int


@deserialize.downcast_identifier(DowncastableBase, "bar")
class Bar(DowncastableBase, SomeRandomBase):
    """Downcastable class."""

    two: int


class Baz(DowncastableBase):
    """Downcastable class with no identifier."""

    three: int


class DowncastingTestSuite(unittest.TestCase):
    """Deserialization downcasting test cases."""

    def test_downcasting_foo(self):
        """Test that we can deserialize a simple class."""

        data = {"type_name": "foo", "one": 1}

        result = deserialize.deserialize(DowncastableBase, data)
        self.assertTrue(isinstance(result, Foo))
        self.assertEqual(result.one, 1)
        self.assertEqual(result.type_name, "foo")

    def test_downcasting_bar(self):
        """Test that we can deserialize a class with multiple bases."""

        data = {"type_name": "bar", "two": 2, "hello": "world"}

        result = deserialize.deserialize(DowncastableBase, data)
        self.assertTrue(isinstance(result, Bar))
        self.assertEqual(result.two, 2)
        self.assertEqual(result.type_name, "bar")

    def test_downcasting_baz(self):
        """Test that non-declared subclasses don't deserialize."""

        data = {"type_name": "baz", "three": 3}

        with self.assertRaises(deserialize.UndefinedDowncastException):
            _ = deserialize.deserialize(DowncastableBase, data)

    def test_downcasting_multi(self):
        """Test that we can deserialize a simple class."""

        casts = [("foo", Foo), ("bar", Bar), ("baz", Baz)]
        data = {"one": 1, "two": 2, "three": 3, "hello": "world"}

        for identifier, subclass in casts:
            specific_data = copy.deepcopy(data)
            specific_data["type_name"] = identifier

            if identifier == "baz":
                with self.assertRaises(deserialize.UndefinedDowncastException):
                    _ = deserialize.deserialize(DowncastableBase, specific_data)
                continue

            result = deserialize.deserialize(DowncastableBase, specific_data)

            self.assertTrue(isinstance(result, subclass))
            self.assertEqual(result.type_name, identifier)

            if isinstance(result, Foo):
                self.assertEqual(result.one, 1)
            elif isinstance(result, Bar):
                self.assertEqual(result.two, 2)
                self.assertEqual(result.hello, "world")
            else:
                raise Exception(f"Unexpected type: {type(result)}")

    def test_downcasting_nested(self):
        """Test that we can deserialize a nested downcast classes."""

        data = [{"type_name": "foo", "one": 1}, {"type_name": "bar", "two": 2, "hello": "world"}]

        results = deserialize.deserialize(List[DowncastableBase], data)
        foo = results[0]
        bar = results[1]

        self.assertTrue(isinstance(foo, Foo))
        self.assertTrue(isinstance(bar, Bar))

        self.assertEqual(foo.one, 1)
        self.assertEqual(bar.two, 2)

        self.assertEqual(foo.type_name, "foo")
        self.assertEqual(bar.type_name, "bar")
