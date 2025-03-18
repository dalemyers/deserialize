"""Test downcasting."""

import copy
import os
import sys
from typing import List

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import (
    deserialize,
    downcast_field,
    downcast_identifier,
    allow_downcast_fallback,
    UndefinedDowncastException,
)

# pylint: enable=wrong-import-position

# pylint: disable=blacklisted-name


class SomeRandomBase:
    """A sample base class."""

    hello: str


@downcast_field("type_name")
class DowncastableBase:
    """A downcastable base class."""

    type_name: str


@downcast_identifier(DowncastableBase, "foo")
class Foo(DowncastableBase):
    """Downcastable class."""

    one: int


@downcast_identifier(DowncastableBase, "bar")
class Bar(DowncastableBase, SomeRandomBase):
    """Downcastable class."""

    two: int


class Baz(DowncastableBase):
    """Downcastable class with no identifier."""

    three: int


def test_downcasting_foo() -> None:
    """Test that we can deserialize a simple class."""

    data = {"type_name": "foo", "one": 1}

    result = deserialize(DowncastableBase, data)
    assert isinstance(result, Foo)
    assert result.one == 1
    assert result.type_name == "foo"


def test_downcasting_bar() -> None:
    """Test that we can deserialize a class with multiple bases."""

    data = {"type_name": "bar", "two": 2, "hello": "world"}

    result = deserialize(DowncastableBase, data)
    assert isinstance(result, Bar)
    assert result.two == 2
    assert result.type_name == "bar"


def test_downcasting_baz() -> None:
    """Test that non-declared subclasses don't deserialize."""

    data = {"type_name": "baz", "three": 3}

    with pytest.raises(UndefinedDowncastException):
        _ = deserialize(DowncastableBase, data)


def test_downcasting_multi() -> None:
    """Test that we can deserialize a simple class."""

    casts = [("foo", Foo), ("bar", Bar), ("baz", Baz)]
    data = {"one": 1, "two": 2, "three": 3, "hello": "world"}

    for identifier, subclass in casts:
        specific_data = copy.deepcopy(data)
        specific_data["type_name"] = identifier

        if identifier == "baz":
            with pytest.raises(UndefinedDowncastException):
                _ = deserialize(DowncastableBase, specific_data)
            continue

        result = deserialize(DowncastableBase, specific_data)

        assert isinstance(result, subclass)
        assert result.type_name == identifier

        if isinstance(result, Foo):
            assert result.one == 1
        elif isinstance(result, Bar):
            assert result.two == 2
            assert result.hello == "world"
        else:
            raise TypeError(f"Unexpected type: {type(result)}")


def test_downcasting_nested() -> None:
    """Test that we can deserialize a nested downcast classes."""

    data = [
        {"type_name": "foo", "one": 1},
        {"type_name": "bar", "two": 2, "hello": "world"},
    ]

    results = deserialize(List[DowncastableBase], data)
    foo = results[0]
    bar = results[1]

    assert isinstance(foo, Foo)
    assert isinstance(bar, Bar)

    assert foo.one == 1
    assert bar.two == 2

    assert foo.type_name == "foo"
    assert bar.type_name == "bar"


def test_downcasting_fallback() -> None:
    """Test that we can deserialize a class with a fallback."""

    @downcast_field("type_name")
    @allow_downcast_fallback()
    class MyBase:
        """A downcastable base class."""

        type_name: str

    @downcast_identifier(MyBase, "foo")
    class MyFoo(MyBase):
        """Downcastable class."""

        one: int

    data = [
        {"type_name": "foo", "one": 1},
        {"type_name": "bar", "some_data": 42},
    ]

    results = deserialize(List[MyBase], data)
    foo = results[0]
    bar = results[1]

    assert isinstance(foo, MyFoo)
    assert isinstance(bar, dict)

    assert foo.one == 1
    assert bar["some_data"] == 42

    assert foo.type_name == "foo"
    assert bar["type_name"] == "bar"
