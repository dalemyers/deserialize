"""Test type checks."""

import datetime
import os
import sys
from typing import Callable, Dict, List, Pattern, Union

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import (
    DeserializeException,
    is_typing_type,
    is_union,
    union_types,
    is_list,
    is_dict,
    list_content_type,
    dict_content_types,
)

# pylint: enable=wrong-import-position


def test_is_typing_type() -> None:
    """Test is_typing_type."""

    assert not is_typing_type(int)
    assert not is_typing_type(str)
    assert not is_typing_type(datetime.datetime)
    assert not is_typing_type(float)
    assert not is_typing_type(dict)
    assert not is_typing_type(list)
    assert not is_typing_type(tuple)
    assert not is_typing_type(range)

    assert is_typing_type(List)
    assert is_typing_type(list[int])
    assert is_typing_type(Dict)
    assert is_typing_type(dict[str, str])
    assert is_typing_type(int | None)
    assert is_typing_type(list[List])
    assert is_typing_type(tuple[str, int])
    assert is_typing_type(Union[str, None])
    assert is_typing_type(Union[str, int])
    assert is_typing_type(Callable)
    assert is_typing_type(Pattern)


def test_is_union() -> None:
    """Test is_union."""

    assert is_union(Union[int, None])
    assert is_union(Union[dict[str, str], None])
    assert is_union(Union[int, str])
    assert is_union(Union[str, int])
    assert is_union(Union[int, Union[int, str]])
    assert is_union(Union[Union[str, int], int])

    assert not is_union(int)
    assert not is_union(list[int])
    assert not is_union(dict[str, str])
    assert not is_union(tuple[int | None, int])

    # The typing module doesn't let you create either of these.
    assert not is_union(Union[None])
    assert not is_union(Union[None, None])


def test_union_types() -> None:
    """Test union_types."""

    assert union_types(Union[str, int], "") == {str, int}
    assert union_types(Union[dict[str, str], int], "") == {
        dict[str, str],
        int,
    }
    assert union_types(Union[int, None], "") == {int, type(None)}
    assert union_types(Union[None, int], "") == {type(None), int}

    # X | None | None == X | None
    assert union_types(Union[Union[int, None], None], "") == {
        int,
        type(None),
    }
    assert union_types(Union[None, str | None], "") == {type(None), str}

    with pytest.raises(DeserializeException):
        _ = union_types(int, "")

    with pytest.raises(DeserializeException):
        _ = union_types(tuple[int | None, int], "")


def test_is_list() -> None:
    """Test is_list."""

    assert is_list(list[int])
    assert is_list(list[str])
    assert is_list(list[list[int]])
    assert is_list(list[type(None)])  # type: ignore
    assert is_list(list[dict[str, str]])
    assert is_list(list[str | None])
    assert is_list(list[Union[str, int]])
    assert is_list(list)

    assert not is_list(int)
    assert not is_list(list[int] | None)
    assert not is_list(str | None)
    assert not is_list(type(None))


def test_list_content_type() -> None:
    """Test list_content_type."""

    assert list_content_type(list[int], "") == int
    assert list_content_type(list[str], "") == str
    assert list_content_type(list[dict[str, str]], "") == dict[str, str]
    assert list_content_type(list[int | None], "") == int | None
    assert list_content_type(list[list[int]], "") == list[int]

    with pytest.raises(TypeError):
        _ = list_content_type(int, "")

    with pytest.raises(TypeError):
        _ = list_content_type(tuple[list[int], int], "")


def test_is_dict() -> None:
    """Test is_dict."""

    assert is_dict(dict)
    assert is_dict(dict[int, int])
    assert is_dict(dict[str, int])
    assert is_dict(dict[str, dict[str, str]])
    assert is_dict(dict[int, str | None])
    assert is_dict(dict[dict[int, str], dict[str, int]])

    assert not is_dict(int)
    assert not is_dict(dict[int, int] | None)
    assert not is_dict(tuple[str, int])


def test_dict_content_types() -> None:
    """Test dict_content_types."""

    assert dict_content_types(dict[int, int], "") == (int, int)
    assert dict_content_types(dict[str, int], "") == (str, int)
    assert dict_content_types(dict[str, dict[str, str]], "") == (
        str,
        dict[str, str],
    )
    assert dict_content_types(dict[dict[int, int], dict[str, str]], "") == (
        dict[int, int],
        dict[str, str],
    )
    assert dict_content_types(dict[int, str | None], "") == (
        int,
        str | None,
    )

    with pytest.raises(TypeError):
        _ = dict_content_types(int, "")

    with pytest.raises(TypeError):
        _ = dict_content_types(tuple[list[int], int], "")
