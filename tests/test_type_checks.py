"""Test type checks."""

import datetime
import os
import sys
from typing import Callable, Dict, List, Optional, Pattern, Tuple, Union

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


def test_is_typing_type():
    """Test is_typing_type."""

    assert not deserialize.is_typing_type(int)
    assert not deserialize.is_typing_type(str)
    assert not deserialize.is_typing_type(datetime.datetime)
    assert not deserialize.is_typing_type(float)
    assert not deserialize.is_typing_type(dict)
    assert not deserialize.is_typing_type(list)
    assert not deserialize.is_typing_type(tuple)
    assert not deserialize.is_typing_type(range)

    assert deserialize.is_typing_type(List)
    assert deserialize.is_typing_type(List[int])
    assert deserialize.is_typing_type(Dict)
    assert deserialize.is_typing_type(Dict[str, str])
    assert deserialize.is_typing_type(Optional[int])
    assert deserialize.is_typing_type(List[List])
    assert deserialize.is_typing_type(Tuple[str, int])
    assert deserialize.is_typing_type(Union[str, None])
    assert deserialize.is_typing_type(Union[str, int])
    assert deserialize.is_typing_type(Callable)
    assert deserialize.is_typing_type(Pattern)


def test_is_union():
    """Test is_union."""

    assert deserialize.is_union(Union[int, None])
    assert deserialize.is_union(Union[Dict[str, str], None])
    assert deserialize.is_union(Union[int, str])
    assert deserialize.is_union(Union[str, int])
    assert deserialize.is_union(Union[int, Union[int, str]])
    assert deserialize.is_union(Union[Union[str, int], int])

    assert not deserialize.is_union(int)
    assert not deserialize.is_union(List[int])
    assert not deserialize.is_union(Dict[str, str])
    assert not deserialize.is_union(Tuple[Optional[int], int])

    # The typing module doesn't let you create either of these.
    assert not deserialize.is_union(Union[None])
    assert not deserialize.is_union(Union[None, None])


def test_union_types():
    """Test union_types."""

    assert deserialize.union_types(Union[str, int], "") == {str, int}
    assert deserialize.union_types(Union[Dict[str, str], int], "") == {Dict[str, str], int}
    assert deserialize.union_types(Union[int, None], "") == {int, type(None)}
    assert deserialize.union_types(Union[None, int], "") == {type(None), int}

    # Optional[Optional[X]] == Optional[X]
    assert deserialize.union_types(Union[Union[int, None], None], "") == {int, type(None)}
    assert deserialize.union_types(Union[None, Optional[str]], "") == {type(None), str}

    with pytest.raises(deserialize.DeserializeException):
        _ = deserialize.union_types(int, "")

    with pytest.raises(deserialize.DeserializeException):
        _ = deserialize.union_types(Tuple[Optional[int], int], "")


def test_is_list():
    """Test is_list."""

    assert deserialize.is_list(List[int])
    assert deserialize.is_list(List[str])
    assert deserialize.is_list(List[List[int]])
    assert deserialize.is_list(List[type(None)])
    assert deserialize.is_list(List[Dict[str, str]])
    assert deserialize.is_list(List[Optional[str]])
    assert deserialize.is_list(List[Union[str, int]])

    assert not deserialize.is_list(int)
    assert not deserialize.is_list(list)
    assert not deserialize.is_list(Optional[List[int]])
    assert not deserialize.is_list(Optional[str])
    assert not deserialize.is_list(type(None))


def test_list_content_type():
    """Test list_content_type."""

    assert deserialize.list_content_type(List[int], "") == int
    assert deserialize.list_content_type(List[str], "") == str
    assert deserialize.list_content_type(List[Dict[str, str]], "") == Dict[str, str]
    assert deserialize.list_content_type(List[Optional[int]], "") == Optional[int]
    assert deserialize.list_content_type(List[List[int]], "") == List[int]

    with pytest.raises(TypeError):
        _ = deserialize.list_content_type(int, "")

    with pytest.raises(TypeError):
        _ = deserialize.list_content_type(Tuple[List[int], int], "")


def test_is_dict():
    """Test is_dict."""

    assert deserialize.is_dict(dict)
    assert deserialize.is_dict(Dict[int, int])
    assert deserialize.is_dict(Dict[str, int])
    assert deserialize.is_dict(Dict[str, Dict[str, str]])
    assert deserialize.is_dict(Dict[int, Optional[str]])
    assert deserialize.is_dict(Dict[Dict[int, str], Dict[str, int]])

    assert not deserialize.is_dict(int)
    assert not deserialize.is_dict(Optional[Dict[int, int]])
    assert not deserialize.is_dict(Tuple[str, int])


def test_dict_content_types():
    """Test dict_content_types."""

    assert deserialize.dict_content_types(Dict[int, int], "") == (int, int)
    assert deserialize.dict_content_types(Dict[str, int], "") == (str, int)
    assert deserialize.dict_content_types(Dict[str, Dict[str, str]], "") == (str, Dict[str, str])
    assert deserialize.dict_content_types(Dict[Dict[int, int], Dict[str, str]], "") == (
        Dict[int, int],
        Dict[str, str],
    )
    assert deserialize.dict_content_types(Dict[int, Optional[str]], "") == (int, Optional[str])

    with pytest.raises(TypeError):
        _ = deserialize.dict_content_types(int, "")

    with pytest.raises(TypeError):
        _ = deserialize.dict_content_types(Tuple[List[int], int], "")
