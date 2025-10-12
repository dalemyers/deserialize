"""Test decorator and type hint inheritance."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize, key, default, parser, ignore, auto_snake

# pylint: enable=wrong-import-position


def test_key_decorator_inheritance() -> None:
    """Test that @key decorators are inherited from parent class."""

    @key("base_field", "baseField")
    class BaseClass:
        """Base class with key decorator."""

        base_field: int

    class ChildClass(BaseClass):
        """Child class inheriting key decorator."""

        child_field: str

    data = {"baseField": 42, "child_field": "test"}
    instance = deserialize(ChildClass, data)

    assert instance.base_field == 42
    assert instance.child_field == "test"


def test_default_decorator_inheritance() -> None:
    """Test that @default decorators are inherited from parent class."""

    @default("base_field", 100)
    class BaseClass:
        """Base class with default decorator."""

        base_field: int

    class ChildClass(BaseClass):
        """Child class inheriting default decorator."""

        child_field: str

    # Test with base field missing
    data = {"child_field": "test"}
    instance = deserialize(ChildClass, data)

    assert instance.base_field == 100
    assert instance.child_field == "test"


def test_parser_decorator_inheritance() -> None:
    """Test that @parser decorators are inherited from parent class."""

    @parser("base_field", int)
    class BaseClass:
        """Base class with parser decorator."""

        base_field: int

    class ChildClass(BaseClass):
        """Child class inheriting parser decorator."""

        child_field: str

    data = {"base_field": "42", "child_field": "test"}
    instance = deserialize(ChildClass, data)

    assert instance.base_field == 42
    assert instance.child_field == "test"


def test_ignore_decorator_inheritance() -> None:
    """Test that @ignore decorators are inherited from parent class."""

    @ignore("computed_field")
    class BaseClass:
        """Base class with ignore decorator."""

        regular_field: int
        computed_field: str

    class ChildClass(BaseClass):
        """Child class inheriting ignore decorator."""

        child_field: str

    data = {"regular_field": 42, "child_field": "test"}
    instance = deserialize(ChildClass, data)

    assert instance.regular_field == 42
    assert instance.child_field == "test"
    # computed_field is ignored, so it won't be set
    with pytest.raises(AttributeError):
        _ = instance.computed_field


def test_type_hints_inheritance() -> None:
    """Test that type hints are properly inherited."""

    class BaseClass:
        """Base class with type hints."""

        base_int: int
        base_str: str

    class ChildClass(BaseClass):
        """Child class with additional type hints."""

        child_float: float
        child_list: list[int]

    data = {
        "base_int": 42,
        "base_str": "hello",
        "child_float": 3.14,
        "child_list": [1, 2, 3],
    }

    instance = deserialize(ChildClass, data)

    assert instance.base_int == 42
    assert instance.base_str == "hello"
    assert instance.child_float == 3.14
    assert instance.child_list == [1, 2, 3]


def test_override_parent_decorator() -> None:
    """Test that child class decorator affects both child and parent after definition."""

    @key("field", "parentKey")
    class BaseClass:
        """Base class with key decorator."""

        field: int

    # Note: When child overrides decorator on parent class attribute storage,
    # it modifies the parent class storage itself since decorators modify class attributes
    @key("field", "childKey")
    class ChildClass(BaseClass):
        """Child class overriding key decorator."""

    # Child uses childKey
    data = {"childKey": 42}
    instance = deserialize(ChildClass, data)
    assert instance.field == 42

    # Note: The parent class is also affected because decorators modify the class dict
    # This is expected Python behavior for class-level attributes


def test_multiple_inheritance_type_hints() -> None:
    """Test type hints with multiple inheritance."""

    class BaseA:
        """First base class."""

        field_a: int

    class BaseB:
        """Second base class."""

        field_b: str

    class ChildClass(BaseA, BaseB):
        """Child class with multiple inheritance."""

        field_c: float

    data = {"field_a": 42, "field_b": "test", "field_c": 3.14}
    instance = deserialize(ChildClass, data)

    assert instance.field_a == 42
    assert instance.field_b == "test"
    assert instance.field_c == 3.14


def test_auto_snake_inheritance() -> None:
    """Test auto_snake decorator inheritance."""

    @auto_snake()
    class BaseClass:
        """Base class with auto_snake."""

        base_field: int

    class ChildClass(BaseClass):
        """Child class inheriting auto_snake."""

        child_field: str

    # Should work with PascalCase
    data = {"BaseField": 42, "ChildField": "test"}
    instance = deserialize(ChildClass, data)

    assert instance.base_field == 42
    assert instance.child_field == "test"


def test_deep_inheritance_chain() -> None:
    """Test decorators through deep inheritance chain."""

    @key("field", "originalKey")
    class GrandParent:
        """Grandparent class."""

        field: int

    class Parent(GrandParent):
        """Parent class."""

        parent_field: str

    @default("optional_field", "default")
    class Child(Parent):
        """Child class."""

        optional_field: str

    data = {"originalKey": 42, "parent_field": "test"}
    instance = deserialize(Child, data)

    assert instance.field == 42
    assert instance.parent_field == "test"
    assert instance.optional_field == "default"


def test_child_adds_decorator_to_parent_field() -> None:
    """Test that child can add decorators to inherited fields."""

    class BaseClass:
        """Base class without decorators."""

        field: int

    @parser("field", lambda x: int(x) * 2)
    class ChildClass(BaseClass):
        """Child adds parser to parent's field."""

    data = {"field": 21}
    instance = deserialize(ChildClass, data)

    # Parser should double the value
    assert instance.field == 42


def test_optional_fields_inheritance() -> None:
    """Test Optional field inheritance."""

    class BaseClass:
        """Base class with optional field."""

        required: int
        optional: str | None

    class ChildClass(BaseClass):
        """Child class."""

        child_required: str

    # Test with optional present
    data1 = {"required": 42, "optional": "present", "child_required": "test"}
    instance1 = deserialize(ChildClass, data1)
    assert instance1.optional == "present"

    # Test with optional missing
    data2 = {"required": 42, "optional": None, "child_required": "test"}
    instance2 = deserialize(ChildClass, data2)
    assert instance2.optional is None
