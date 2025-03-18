"""Test type checks."""

import datetime
import os
import sys
from typing import Callable, Dict, List, Optional, Pattern, Tuple, Union

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
    assert is_typing_type(List[int])
    assert is_typing_type(Dict)
    assert is_typing_type(Dict[str, str])
    assert is_typing_type(Optional[int])
    assert is_typing_type(List[List])
    assert is_typing_type(Tuple[str, int])
    assert is_typing_type(Union[str, None])
    assert is_typing_type(Union[str, int])
    assert is_typing_type(Callable)
    assert is_typing_type(Pattern)


def test_is_union() -> None:
    """Test is_union."""

    assert is_union(Union[int, None])
    assert is_union(Union[Dict[str, str], None])
    assert is_union(Union[int, str])
    assert is_union(Union[str, int])
    assert is_union(Union[int, Union[int, str]])
    assert is_union(Union[Union[str, int], int])

    assert not is_union(int)
    assert not is_union(List[int])
    assert not is_union(Dict[str, str])
    assert not is_union(Tuple[Optional[int], int])

    # The typing module doesn't let you create either of these.
    assert not is_union(Union[None])
    assert not is_union(Union[None, None])


def test_union_types() -> None:
    """Test union_types."""

    assert union_types(Union[str, int], "") == {str, int}
    assert union_types(Union[Dict[str, str], int], "") == {
        Dict[str, str],
        int,
    }
    assert union_types(Union[int, None], "") == {int, type(None)}
    assert union_types(Union[None, int], "") == {type(None), int}

    # Optional[Optional[X]] == Optional[X]
    assert union_types(Union[Union[int, None], None], "") == {
        int,
        type(None),
    }
    assert union_types(Union[None, Optional[str]], "") == {type(None), str}

    with pytest.raises(DeserializeException):
        _ = union_types(int, "")

    with pytest.raises(DeserializeException):
        _ = union_types(Tuple[Optional[int], int], "")


def test_is_list() -> None:
    """Test is_list."""

    assert is_list(List[int])
    assert is_list(List[str])
    assert is_list(List[List[int]])
    assert is_list(List[type(None)])  # type: ignore
    assert is_list(List[Dict[str, str]])
    assert is_list(List[Optional[str]])
    assert is_list(List[Union[str, int]])
    assert is_list(list)

    assert not is_list(int)
    assert not is_list(Optional[List[int]])
    assert not is_list(Optional[str])
    assert not is_list(type(None))


def test_list_content_type() -> None:
    """Test list_content_type."""

    assert list_content_type(List[int], "") == int
    assert list_content_type(List[str], "") == str
    assert list_content_type(List[Dict[str, str]], "") == Dict[str, str]
    assert list_content_type(List[Optional[int]], "") == Optional[int]
    assert list_content_type(List[List[int]], "") == List[int]

    with pytest.raises(TypeError):
        _ = list_content_type(int, "")

    with pytest.raises(TypeError):
        _ = list_content_type(Tuple[List[int], int], "")


def test_is_dict() -> None:
    """Test is_dict."""

    assert is_dict(dict)
    assert is_dict(Dict[int, int])
    assert is_dict(Dict[str, int])
    assert is_dict(Dict[str, Dict[str, str]])
    assert is_dict(Dict[int, Optional[str]])
    assert is_dict(Dict[Dict[int, str], Dict[str, int]])

    assert not is_dict(int)
    assert not is_dict(Optional[Dict[int, int]])
    assert not is_dict(Tuple[str, int])


def test_dict_content_types() -> None:
    """Test dict_content_types."""

    assert dict_content_types(Dict[int, int], "") == (int, int)
    assert dict_content_types(Dict[str, int], "") == (str, int)
    assert dict_content_types(Dict[str, Dict[str, str]], "") == (
        str,
        Dict[str, str],
    )
    assert dict_content_types(Dict[Dict[int, int], Dict[str, str]], "") == (
        Dict[int, int],
        Dict[str, str],
    )
    assert dict_content_types(Dict[int, Optional[str]], "") == (
        int,
        Optional[str],
    )

    with pytest.raises(TypeError):
        _ = dict_content_types(int, "")

    with pytest.raises(TypeError):
        _ = dict_content_types(Tuple[List[int], int], "")
