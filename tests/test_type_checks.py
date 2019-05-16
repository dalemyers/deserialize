"""Test type checks."""

import datetime
import os
import sys
from typing import Callable, Dict, List, Optional, Pattern, Tuple, Union
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#pylint: disable=wrong-import-position
import deserialize
#pylint: enable=wrong-import-position



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


    def test_is_optional(self):
        """Test is_optional."""

        self.assertTrue(deserialize.is_optional(Optional[int]))
        self.assertTrue(deserialize.is_optional(Optional[str]))
        self.assertTrue(deserialize.is_optional(Optional[Dict[str, str]]))

        # Since Optional[T] == Union[T, None] these should pass
        self.assertTrue(deserialize.is_optional(Union[int, None]))
        self.assertTrue(deserialize.is_optional(Union[None, int]))

        self.assertFalse(deserialize.is_optional(int))
        self.assertFalse(deserialize.is_optional(List[int]))
        self.assertFalse(deserialize.is_optional(Dict[str, str]))
        self.assertFalse(deserialize.is_optional(Tuple[Optional[int], int]))

        # The typing module doesn't let you create either of these.
        self.assertFalse(deserialize.is_optional(Optional[None]))
        self.assertFalse(deserialize.is_optional(Union[None, None]))


    def test_optional_content_type(self):
        """Test optional_content_type."""

        self.assertEqual(deserialize.optional_content_type(Optional[int]), int)
        self.assertEqual(deserialize.optional_content_type(Optional[str]), str)
        self.assertEqual(deserialize.optional_content_type(Optional[Dict[str, str]]), Dict[str, str])
        self.assertEqual(deserialize.optional_content_type(Union[int, None]), int)
        self.assertEqual(deserialize.optional_content_type(Union[None, int]), int)

        # Optional[Optional[X]] == Optional[X]
        self.assertEqual(deserialize.optional_content_type(Optional[Optional[int]]), int)
        self.assertEqual(deserialize.optional_content_type(Union[Optional[str], None]), str)
        self.assertEqual(deserialize.optional_content_type(Union[None, Optional[str]]), str)
        self.assertEqual(deserialize.optional_content_type(Union[None, Union[str, None]]), str)

        with self.assertRaises(TypeError):
            _ = deserialize.optional_content_type(int)

        with self.assertRaises(TypeError):
            _ = deserialize.optional_content_type(Tuple[Optional[int], int])


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
        self.assertEqual(deserialize.list_content_type(List[Dict[str, str]]), Dict[str, str])
        self.assertEqual(deserialize.list_content_type(List[Optional[int]]), Optional[int])
        self.assertEqual(deserialize.list_content_type(List[List[int]]), List[int])

        with self.assertRaises(TypeError):
            _ = deserialize.list_content_type(int)

        with self.assertRaises(TypeError):
            _ = deserialize.list_content_type(Tuple[List[int], int])


    def test_is_dict(self):
        """Test is_dict."""

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
        self.assertEqual(deserialize.dict_content_types(Dict[str, Dict[str, str]]), (str, Dict[str, str]))
        self.assertEqual(deserialize.dict_content_types(Dict[Dict[int, int], Dict[str, str]]), (Dict[int, int], Dict[str, str]))
        self.assertEqual(deserialize.dict_content_types(Dict[int, Optional[str]]), (int, Optional[str]))

        with self.assertRaises(TypeError):
            _ = deserialize.dict_content_types(int)

        with self.assertRaises(TypeError):
            _ = deserialize.dict_content_types(Tuple[List[int], int])
