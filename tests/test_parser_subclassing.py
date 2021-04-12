"""Test deserializing."""

import decimal
import os
import sys
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


def _money_amount(value: Any):
    return decimal.Decimal(value) if value else None


@deserialize.parser("a", _money_amount)
class Base:
    a: decimal.Decimal


class Foo(Base):
    b: str


@deserialize.parser("b", _money_amount)
class Bar(Base):
    b: decimal.Decimal


class Baz(Bar):
    pass


def test_deserialize_base():
    deserialize.deserialize(Base, {"a": 1.23})


def test_deserialize_foo():
    deserialize.deserialize(Foo, {"a": 1.23, "b": "b"})


def test_deserialize_bar():
    deserialize.deserialize(Bar, {"a": 1.23, "b": 1.23})


def test_deserialize_baz():
    deserialize.deserialize(Bar, {"a": 1.23, "b": 1.23})
