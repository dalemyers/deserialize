"""Test deserializing."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import camel_case, pascal_case

# pylint: enable=wrong-import-position


def test_camel_case() -> None:
    """Test that camel casing is applied correctly."""

    assert camel_case("hello_world") == "helloWorld"
    assert camel_case("hello") == "hello"
    assert camel_case("h") == "h"
    assert camel_case("") == ""
    assert camel_case("this_is_a_really_long_string") == "thisIsAReallyLongString"
    assert camel_case("1_word") == "1Word"
    assert camel_case("_") == ""
    assert camel_case("CamelCase") == "camelcase"
    assert camel_case("HELLO") == "hello"
    assert camel_case("HELLO_WORLD") == "helloWorld"


def test_pascal_case() -> None:
    """Test that pascal casing is applied correctly."""
    assert pascal_case("hello_world") == "HelloWorld"
    assert pascal_case("hello") == "Hello"
    assert pascal_case("h") == "H"
    assert pascal_case("") == ""
    assert pascal_case("this_is_a_really_long_string") == "ThisIsAReallyLongString"
    assert pascal_case("1_word") == "1Word"
    assert pascal_case("_") == ""
    assert pascal_case("CamelCase") == "Camelcase"
    assert pascal_case("HELLO") == "Hello"
    assert pascal_case("HELLO_WORLD") == "HelloWorld"
