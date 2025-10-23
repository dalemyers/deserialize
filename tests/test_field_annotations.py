"""Test Field-based configuration using Annotated type hints."""

# pylint: disable=missing-class-docstring,import-outside-toplevel

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize, Field, Annotated

# pylint: enable=wrong-import-position


def test_field_alias() -> None:
    """Test that Field alias works like @key decorator."""

    class User:
        user_id: Annotated[int, Field(alias="userId")]
        user_name: Annotated[str, Field(alias="userName")]

    data = {"userId": 123, "userName": "john_doe"}
    user = deserialize(User, data)

    assert user.user_id == 123
    assert user.user_name == "john_doe"


def test_field_default() -> None:
    """Test that Field default works like @default decorator."""

    class Config:
        name: str
        timeout: Annotated[int, Field(default=30)]
        enabled: Annotated[bool, Field(default=True)]

    data = {"name": "test"}
    config = deserialize(Config, data)

    assert config.name == "test"
    assert config.timeout == 30
    assert config.enabled is True


def test_field_default_none() -> None:
    """Test that None can be a valid default value."""

    class Data:
        """Test data class."""

        value: Annotated[str | None, Field(default=None)]

    data: dict[str, str] = {}
    result = deserialize(Data, data)

    assert result.value is None


def test_field_parser() -> None:
    """Test that Field parser works like @parser decorator."""

    def double(x: int) -> int:
        return x * 2

    class Numbers:
        value: Annotated[int, Field(parser=double)]

    data = {"value": 5}
    result = deserialize(Numbers, data)

    assert result.value == 10


def test_field_ignore() -> None:
    """Test that Field ignore works like @ignore decorator."""

    class Data:
        public: int
        _internal: Annotated[str, Field(ignore=True)]

    data = {"public": 42, "_internal": "should_be_ignored"}
    result = deserialize(Data, data)

    assert result.public == 42
    assert not hasattr(result, "_internal")


def test_field_multiple_options() -> None:
    """Test Field with multiple options combined."""

    def parse_upper(s: str) -> str:
        return s.upper()

    class Item:
        item_id: Annotated[int, Field(alias="id")]
        name: Annotated[str, Field(alias="itemName", parser=parse_upper)]
        count: Annotated[int, Field(alias="quantity", default=1)]

    data = {"id": 456, "itemName": "widget"}
    item = deserialize(Item, data)

    assert item.item_id == 456
    assert item.name == "WIDGET"
    assert item.count == 1


def test_field_with_complex_types() -> None:
    """Test Field with complex nested types."""

    class Address:
        street: Annotated[str, Field(alias="streetAddress")]
        city: str

    class Person:
        name: str
        address: Annotated[Address, Field(alias="homeAddress")]

    data = {"name": "John", "homeAddress": {"streetAddress": "123 Main St", "city": "Boston"}}

    person = deserialize(Person, data)
    assert person.name == "John"
    assert person.address.street == "123 Main St"
    assert person.address.city == "Boston"


def test_field_with_list() -> None:
    """Test Field with List types."""

    class Item:
        item_id: Annotated[int, Field(alias="id")]

    class Order:
        order_id: Annotated[int, Field(alias="orderId")]
        items: Annotated[list[Item], Field(alias="orderItems")]

    data = {"orderId": 789, "orderItems": [{"id": 1}, {"id": 2}]}

    order = deserialize(Order, data)
    assert order.order_id == 789
    assert len(order.items) == 2
    assert order.items[0].item_id == 1
    assert order.items[1].item_id == 2


def test_field_fallback_to_decorators() -> None:
    """Test that decorators still work when Field is not used."""

    from deserialize import key, default

    @key("value", "val")
    @default("count", 10)
    class OldStyle:
        value: int
        count: int

    data = {"val": 5}
    result = deserialize(OldStyle, data)

    assert result.value == 5
    assert result.count == 10


def test_field_takes_precedence_over_decorators() -> None:
    """Test that Field takes precedence when both are present."""

    from deserialize import key, default

    @key("value", "decoratorKey")
    @default("value", 999)
    class Mixed:
        """Test class with mixed configuration."""

        value: Annotated[int, Field(alias="fieldKey", default=42)]

    # Should use Field's alias and default, not decorator's
    data: dict[str, int] = {"fieldKey": 100}
    result = deserialize(Mixed, data)
    assert result.value == 100

    # When fieldKey is missing, should use Field's default
    data2: dict[str, int] = {}
    result2 = deserialize(Mixed, data2)
    assert result2.value == 42


def test_field_mixed_with_regular_fields() -> None:
    """Test mixing Field-annotated and regular fields."""

    class Mixed:
        regular_field: int
        annotated_field: Annotated[str, Field(alias="annotatedKey")]
        another_regular: bool

    data = {"regular_field": 1, "annotatedKey": "test", "another_regular": True}

    result = deserialize(Mixed, data)
    assert result.regular_field == 1
    assert result.annotated_field == "test"
    assert result.another_regular is True


def test_field_with_optional() -> None:
    """Test Field with Optional types."""

    class Data:
        required: Annotated[str, Field(alias="req")]
        optional: Annotated[int | None, Field(alias="opt")]

    data = {"req": "test", "opt": None}
    result = deserialize(Data, data)

    assert result.required == "test"
    assert result.optional is None


def test_field_repr() -> None:
    """Test Field __repr__ shows configuration."""

    field1 = Field(alias="test")
    assert "alias='test'" in repr(field1)

    field2 = Field(default=42)
    assert "default=42" in repr(field2)

    field3 = Field(parser=str.upper)
    assert "parser=" in repr(field3)

    field4 = Field(ignore=True)
    assert "ignore=True" in repr(field4)

    field5 = Field()
    assert repr(field5) == "Field()"


def test_field_has_default_method() -> None:
    """Test Field.has_default() correctly distinguishes no default from None default."""

    field_no_default = Field()
    assert field_no_default.has_default() is False

    field_none_default = Field(default=None)
    assert field_none_default.has_default() is True
    assert field_none_default.default is None

    field_zero_default = Field(default=0)
    assert field_zero_default.has_default() is True
    assert field_zero_default.default == 0


def test_field_parser_with_alias() -> None:
    """Test parser is applied after alias resolution."""

    def add_prefix(s: str) -> str:
        return f"PREFIX_{s}"

    class Data:
        value: Annotated[str, Field(alias="val", parser=add_prefix)]

    data = {"val": "test"}
    result = deserialize(Data, data)

    assert result.value == "PREFIX_test"


def test_field_works_with_auto_snake() -> None:
    """Test that Field works with @auto_snake decorator."""

    from deserialize import auto_snake

    @auto_snake()
    class User:
        """Test user class."""

        user_id: int  # Will match userId or UserId
        email: Annotated[str, Field(alias="emailAddress")]  # Explicit override

    data = {"userId": 123, "emailAddress": "test@example.com"}
    user = deserialize(User, data)

    assert user.user_id == 123
    assert user.email == "test@example.com"
