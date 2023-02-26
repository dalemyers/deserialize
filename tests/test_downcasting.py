"""Test downcasting."""

import copy
import os
import sys
from typing import List

import pytest

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


def test_downcasting_foo():
    """Test that we can deserialize a simple class."""

    data = {"type_name": "foo", "one": 1}

    result = deserialize.deserialize(DowncastableBase, data)
    assert isinstance(result, Foo)
    assert result.one == 1
    assert result.type_name == "foo"


def test_downcasting_bar():
    """Test that we can deserialize a class with multiple bases."""

    data = {"type_name": "bar", "two": 2, "hello": "world"}

    result = deserialize.deserialize(DowncastableBase, data)
    assert isinstance(result, Bar)
    assert result.two == 2
    assert result.type_name == "bar"


def test_downcasting_baz():
    """Test that non-declared subclasses don't deserialize."""

    data = {"type_name": "baz", "three": 3}

    with pytest.raises(deserialize.UndefinedDowncastException):
        _ = deserialize.deserialize(DowncastableBase, data)


def test_downcasting_multi():
    """Test that we can deserialize a simple class."""

    casts = [("foo", Foo), ("bar", Bar), ("baz", Baz)]
    data = {"one": 1, "two": 2, "three": 3, "hello": "world"}

    for identifier, subclass in casts:
        specific_data = copy.deepcopy(data)
        specific_data["type_name"] = identifier

        if identifier == "baz":
            with pytest.raises(deserialize.UndefinedDowncastException):
                _ = deserialize.deserialize(DowncastableBase, specific_data)
            continue

        result = deserialize.deserialize(DowncastableBase, specific_data)

        assert isinstance(result, subclass)
        assert result.type_name == identifier

        if isinstance(result, Foo):
            assert result.one == 1
        elif isinstance(result, Bar):
            assert result.two == 2
            assert result.hello == "world"
        else:
            raise TypeError(f"Unexpected type: {type(result)}")


def test_downcasting_nested():
    """Test that we can deserialize a nested downcast classes."""

    data = [{"type_name": "foo", "one": 1}, {"type_name": "bar", "two": 2, "hello": "world"}]

    results = deserialize.deserialize(List[DowncastableBase], data)
    foo = results[0]
    bar = results[1]

    assert isinstance(foo, Foo)
    assert isinstance(bar, Bar)

    assert foo.one == 1
    assert bar.two == 2

    assert foo.type_name == "foo"
    assert bar.type_name == "bar"


def test_downcasting_fallback():
    """Test that we can deserialize a class with a fallback."""

    @deserialize.downcast_field("type_name")
    @deserialize.allow_downcast_fallback()
    class MyBase:
        """A downcastable base class."""

        type_name: str

    @deserialize.downcast_identifier(MyBase, "foo")
    class MyFoo(MyBase):
        """Downcastable class."""

        one: int

    data = [
        {"type_name": "foo", "one": 1},
        {"type_name": "bar", "some_data": 42},
    ]

    results = deserialize.deserialize(List[MyBase], data)
    foo = results[0]
    bar = results[1]

    assert isinstance(foo, MyFoo)
    assert isinstance(bar, dict)

    assert foo.one == 1
    assert bar["some_data"] == 42

    assert foo.type_name == "foo"
    assert bar["type_name"] == "bar"
