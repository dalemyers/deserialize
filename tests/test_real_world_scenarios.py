"""Test complex real-world scenarios."""

import datetime
import os
import sys
from typing import Any, Union

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import (
    deserialize,
    key,
    parser,
    default,
    downcast_field,
    downcast_identifier,
    constructed,
    RawStorageMode,
)

# pylint: enable=wrong-import-position


def test_complex_api_response() -> None:
    """Test deserializing a complex API response with multiple features."""

    # Simulating a complex API response with various features
    @downcast_field("event_type")
    class Event:
        """Base event class."""

        event_type: str
        event_id: str

    @downcast_identifier(Event, "user_login")
    class UserLoginEvent(Event):
        """User login event."""

        user_id: int
        ip_address: str

    @downcast_identifier(Event, "user_logout")
    class UserLogoutEvent(Event):
        """User logout event."""

        user_id: int
        session_duration: int

    @key("user_metadata", "userMeta")
    @parser("created_at", datetime.datetime.fromisoformat)
    @default("is_active", True)
    class User:
        """User class with multiple decorators."""

        user_id: int
        username: str
        email: str
        created_at: datetime.datetime
        is_active: bool
        user_metadata: dict[str, Any] | None

    class ApiResponse:
        """Complete API response."""

        success: bool
        user: User
        recent_events: list[Event]
        metadata: dict[str, str]

    # Complex test data
    data = {
        "success": True,
        "user": {
            "user_id": 12345,
            "username": "john_doe",
            "email": "john@example.com",
            "created_at": "2024-01-15T10:30:00",
            "userMeta": {"role": "admin", "department": "engineering"},
        },
        "recent_events": [
            {
                "event_type": "user_login",
                "event_id": "evt_001",
                "user_id": 12345,
                "ip_address": "192.168.1.1",
            },
            {
                "event_type": "user_logout",
                "event_id": "evt_002",
                "user_id": 12345,
                "session_duration": 28800,
            },
        ],
        "metadata": {"version": "1.0", "server": "api-01"},
    }

    # Deserialize with raw storage
    response = deserialize(ApiResponse, data, raw_storage_mode=RawStorageMode.ROOT)

    # Verify basic fields
    assert response.success is True
    assert response.metadata["version"] == "1.0"

    # Verify user with all decorators
    assert response.user.user_id == 12345
    assert response.user.username == "john_doe"
    assert response.user.created_at == datetime.datetime(2024, 1, 15, 10, 30, 0)
    assert response.user.is_active is True  # Default value used
    assert response.user.user_metadata is not None
    assert (
        response.user.user_metadata["role"] == "admin"  # pyright: ignore[reportOptionalSubscript]
    )

    # Verify downcast events
    assert len(response.recent_events) == 2

    login_event = response.recent_events[0]
    assert isinstance(login_event, UserLoginEvent)
    assert login_event.event_type == "user_login"
    assert login_event.user_id == 12345
    assert login_event.ip_address == "192.168.1.1"

    logout_event = response.recent_events[1]
    assert isinstance(logout_event, UserLogoutEvent)
    assert logout_event.event_type == "user_logout"
    assert logout_event.session_duration == 28800

    # Verify raw storage
    assert hasattr(response, "__deserialize_raw__")
    assert (
        response.__deserialize_raw__  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
        == data
    )


def test_complex_ecommerce_scenario() -> None:
    """Test complex e-commerce order structure."""

    @parser("price", float)
    @parser("quantity", int)
    class OrderItem:
        """Order item."""

        product_id: str
        name: str
        price: float
        quantity: int

    def calculate_total(order: "Order"):
        """Calculate order total."""
        order.total = sum(item.price * item.quantity for item in order.items)  # type: ignore

    @key("order_number", "orderNo")
    @parser("order_date", datetime.datetime.fromisoformat)
    @default("status", "pending")
    @default("shipping_cost", 0.0)
    @constructed(calculate_total)
    class Order:
        """Order with constructed total calculation."""

        order_number: str
        order_date: datetime.datetime
        items: list[OrderItem]
        customer_id: int
        status: str
        shipping_cost: float

    data = {
        "orderNo": "ORD-2024-001",
        "order_date": "2024-03-18T10:00:00",
        "items": [
            {"product_id": "PROD-1", "name": "Widget", "price": "29.99", "quantity": "2"},
            {"product_id": "PROD-2", "name": "Gadget", "price": "49.99", "quantity": "1"},
        ],
        "customer_id": 9876,
    }

    order = deserialize(Order, data)

    # Verify all fields
    assert order.order_number == "ORD-2024-001"
    assert order.customer_id == 9876
    assert order.status == "pending"  # Default
    assert order.shipping_cost == 0.0  # Default
    assert len(order.items) == 2

    # Verify constructed total
    assert hasattr(order, "total")
    assert order.total == (  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
        29.99 * 2
    ) + (49.99 * 1)


def test_nested_unions_and_optionals() -> None:
    """Test complex nested unions and optional types."""

    class StringValue:
        """String value wrapper."""

        value: str

    class IntValue:
        """Int value wrapper."""

        value: int

    class Config:
        """Config with complex nested types."""

        settings: dict[str, Union[str, int, StringValue, IntValue]]
        optional_nested: list[dict[str, Union[str, int]] | None] | None

    data = {
        "settings": {
            "timeout": 30,
            "url": "https://api.example.com",
            "wrapped_str": {"value": "wrapped"},
            "wrapped_int": {"value": 42},
        },
        "optional_nested": [
            {"key1": "value1", "key2": 123},
            None,
            {"key3": "value3"},
        ],
    }

    config = deserialize(Config, data)

    assert config.settings["timeout"] == 30
    assert config.settings["url"] == "https://api.example.com"
    assert isinstance(config.settings["wrapped_str"], StringValue)
    assert config.settings["wrapped_str"].value == "wrapped"
    assert isinstance(config.settings["wrapped_int"], IntValue)
    assert config.settings["wrapped_int"].value == 42

    assert config.optional_nested is not None

    assert len(config.optional_nested) == 3
    assert config.optional_nested[0] is not None
    assert config.optional_nested[0]["key1"] == "value1"  # pyright: ignore[reportOptionalSubscript]
    assert config.optional_nested[1] is None
    assert config.optional_nested[2] is not None
    assert config.optional_nested[2]["key3"] == "value3"  # pyright: ignore[reportOptionalSubscript]
