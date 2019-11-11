"""Test type checks."""

import datetime
import os
import sys
from typing import Callable, Dict, List, Optional, Pattern, Tuple, Union
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


class TypeCheckTestSuite(unittest.TestCase):
    """Deserialization type check utility test cases."""

    def test_is_typing_type(self):
        """Test is_typing_type."""

        self.assertFalse(deserialize.is_typing_type(int))
        self.assertFalse(deserialize.is_typing_type(str))
        self.assertFalse(deserialize.is_typing_type(datetime.datetime))
        self.assertFalse(deserialize.is_typing_type(float))
        self.assertFalse(deserialize.is_typing_type(dict))
        self.assertFalse(deserialize.is_typing_type(list))
        self.assertFalse(deserialize.is_typing_type(tuple))
        self.assertFalse(deserialize.is_typing_type(range))

        self.assertTrue(deserialize.is_typing_type(List))
        self.assertTrue(deserialize.is_typing_type(List[int]))
        self.assertTrue(deserialize.is_typing_type(Dict))
        self.assertTrue(deserialize.is_typing_type(Dict[str, str]))
        self.assertTrue(deserialize.is_typing_type(Optional[int]))
        self.assertTrue(deserialize.is_typing_type(List[List]))
        self.assertTrue(deserialize.is_typing_type(Tuple[str, int]))
        self.assertTrue(deserialize.is_typing_type(Union[str, None]))
        self.assertTrue(deserialize.is_typing_type(Union[str, int]))
        self.assertTrue(deserialize.is_typing_type(Callable))
        self.assertTrue(deserialize.is_typing_type(Pattern))

    def test_is_union(self):
        """Test is_union."""

        self.assertTrue(deserialize.is_union(Union[int, None]))
        self.assertTrue(deserialize.is_union(Union[Dict[str, str], None]))
        self.assertTrue(deserialize.is_union(Union[int, str]))
        self.assertTrue(deserialize.is_union(Union[str, int]))
        self.assertTrue(deserialize.is_union(Union[int, Union[int, str]]))
        self.assertTrue(deserialize.is_union(Union[Union[str, int], int]))

        self.assertFalse(deserialize.is_union(int))
        self.assertFalse(deserialize.is_union(List[int]))
        self.assertFalse(deserialize.is_union(Dict[str, str]))
        self.assertFalse(deserialize.is_union(Tuple[Optional[int], int]))

        # The typing module doesn't let you create either of these.
        self.assertFalse(deserialize.is_union(Union[None]))
        self.assertFalse(deserialize.is_union(Union[None, None]))

    def test_union_types(self):
        """Test union_types."""

        self.assertEqual(deserialize.union_types(Union[str, int]), {str, int})
        self.assertEqual(
            deserialize.union_types(Union[Dict[str, str], int]), {Dict[str, str], int}
        )
        self.assertEqual(deserialize.union_types(Union[int, None]), {int, type(None)})
        self.assertEqual(deserialize.union_types(Union[None, int]), {type(None), int})

        # Optional[Optional[X]] == Optional[X]
        self.assertEqual(
            deserialize.union_types(Union[Union[int, None], None]), {int, type(None)}
        )
        self.assertEqual(
            deserialize.union_types(Union[None, Optional[str]]), {type(None), str}
        )

        with self.assertRaises(deserialize.DeserializeException):
            _ = deserialize.union_types(int)

        with self.assertRaises(deserialize.DeserializeException):
            _ = deserialize.union_types(Tuple[Optional[int], int])

    def test_is_list(self):
        """Test is_list."""

        self.assertTrue(deserialize.is_list(List[int]))
        self.assertTrue(deserialize.is_list(List[str]))
        self.assertTrue(deserialize.is_list(List[List[int]]))
        self.assertTrue(deserialize.is_list(List[type(None)]))
        self.assertTrue(deserialize.is_list(List[Dict[str, str]]))
        self.assertTrue(deserialize.is_list(List[Optional[str]]))
        self.assertTrue(deserialize.is_list(List[Union[str, int]]))

        self.assertFalse(deserialize.is_list(int))
        self.assertFalse(deserialize.is_list(list))
        self.assertFalse(deserialize.is_list(Optional[List[int]]))
        self.assertFalse(deserialize.is_list(Optional[str]))
        self.assertFalse(deserialize.is_list(type(None)))

    def test_list_content_type(self):
        """Test list_content_type."""

        self.assertEqual(deserialize.list_content_type(List[int]), int)
        self.assertEqual(deserialize.list_content_type(List[str]), str)
        self.assertEqual(
            deserialize.list_content_type(List[Dict[str, str]]), Dict[str, str]
        )
        self.assertEqual(
            deserialize.list_content_type(List[Optional[int]]), Optional[int]
        )
        self.assertEqual(deserialize.list_content_type(List[List[int]]), List[int])

        with self.assertRaises(TypeError):
            _ = deserialize.list_content_type(int)

        with self.assertRaises(TypeError):
            _ = deserialize.list_content_type(Tuple[List[int], int])

    def test_is_dict(self):
        """Test is_dict."""

        self.assertTrue(deserialize.is_dict(dict))
        self.assertTrue(deserialize.is_dict(Dict[int, int]))
        self.assertTrue(deserialize.is_dict(Dict[str, int]))
        self.assertTrue(deserialize.is_dict(Dict[str, Dict[str, str]]))
        self.assertTrue(deserialize.is_dict(Dict[int, Optional[str]]))
        self.assertTrue(deserialize.is_dict(Dict[Dict[int, str], Dict[str, int]]))

        self.assertFalse(deserialize.is_dict(int))
        self.assertFalse(deserialize.is_dict(Optional[Dict[int, int]]))
        self.assertFalse(deserialize.is_dict(Tuple[str, int]))

    def test_dict_content_types(self):
        """Test dict_content_types."""

        self.assertEqual(deserialize.dict_content_types(Dict[int, int]), (int, int))
        self.assertEqual(deserialize.dict_content_types(Dict[str, int]), (str, int))
        self.assertEqual(
            deserialize.dict_content_types(Dict[str, Dict[str, str]]),
            (str, Dict[str, str]),
        )
        self.assertEqual(
            deserialize.dict_content_types(Dict[Dict[int, int], Dict[str, str]]),
            (Dict[int, int], Dict[str, str]),
        )
        self.assertEqual(
            deserialize.dict_content_types(Dict[int, Optional[str]]),
            (int, Optional[str]),
        )

        with self.assertRaises(TypeError):
            _ = deserialize.dict_content_types(int)

        with self.assertRaises(TypeError):
            _ = deserialize.dict_content_types(Tuple[List[int], int])
