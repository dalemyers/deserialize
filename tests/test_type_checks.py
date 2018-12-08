"""Test type checks."""

import datetime
import os
import sys
from typing import Dict, List, Optional, Tuple
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#pylint: disable=wrong-import-position
import deserialize
#pylint: enable=wrong-import-position



class TypeCheckTestSuite(unittest.TestCase):
    """Deserialization type check utility test cases."""

    def test_is_base_type(self):
        """Test is_base_type."""

        self.assertTrue(deserialize.is_base_type(int))
        self.assertTrue(deserialize.is_base_type(str))
        self.assertTrue(deserialize.is_base_type(datetime.datetime))
        self.assertTrue(deserialize.is_base_type(float))
        self.assertTrue(deserialize.is_base_type(dict))
        self.assertTrue(deserialize.is_base_type(list))

        self.assertFalse(deserialize.is_base_type(List))
        self.assertFalse(deserialize.is_base_type(List[int]))
        self.assertFalse(deserialize.is_base_type(Dict))
        self.assertFalse(deserialize.is_base_type(Dict[str, str]))
        self.assertFalse(deserialize.is_base_type(Optional[int]))
        self.assertFalse(deserialize.is_base_type(List[List]))
        self.assertFalse(deserialize.is_base_type(Tuple[str, int]))


    def test_is_optional(self):
        """Test is_optional."""

        self.assertTrue(deserialize.is_optional(Optional[int]))
        self.assertTrue(deserialize.is_optional(Optional[str]))
        self.assertTrue(deserialize.is_optional(Optional[Dict[str, str]]))

        self.assertFalse(deserialize.is_optional(int))
        self.assertFalse(deserialize.is_optional(List[int]))
        self.assertFalse(deserialize.is_optional(Dict[str, str]))
        self.assertFalse(deserialize.is_optional(Tuple[Optional[int], int]))


    def test_optional_content_type(self):
        """Test optional_content_type."""

        self.assertEqual(deserialize.optional_content_type(Optional[int]), int)
        self.assertEqual(deserialize.optional_content_type(Optional[str]), str)
        self.assertEqual(deserialize.optional_content_type(Optional[Dict[str, str]]), Dict[str, str])

        with self.assertRaises(TypeError):
            _ = deserialize.optional_content_type(int)

        with self.assertRaises(TypeError):
            _ = deserialize.optional_content_type(Tuple[Optional[int], int])


    def test_is_list(self):
        """Test is_list."""

        self.assertTrue(deserialize.is_list(List[int]))
        self.assertTrue(deserialize.is_list(List[str]))
        self.assertTrue(deserialize.is_list(List[Dict[str, str]]))
        self.assertTrue(deserialize.is_list(List[Optional[str]]))

        self.assertFalse(deserialize.is_list(int))
        self.assertFalse(deserialize.is_list(Optional[List[int]]))
        self.assertFalse(deserialize.is_list(Optional[str]))


    def test_list_content_type(self):
        """Test list_content_type."""

        self.assertEqual(deserialize.list_content_type(List[int]), int)
        self.assertEqual(deserialize.list_content_type(List[str]), str)
        self.assertEqual(deserialize.list_content_type(List[Dict[str, str]]), Dict[str, str])

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

        self.assertFalse(deserialize.is_dict(int))
        self.assertFalse(deserialize.is_dict(Optional[Dict[int, int]]))
        self.assertFalse(deserialize.is_dict(Tuple[str, int]))


    def test_dict_content_types(self):
        """Test dict_content_types."""

        self.assertEqual(deserialize.dict_content_types(Dict[int, int]), (int, int))
        self.assertEqual(deserialize.dict_content_types(Dict[str, int]), (str, int))
        self.assertEqual(deserialize.dict_content_types(Dict[str, Dict[str, str]]), (str, Dict[str, str]))
        self.assertEqual(deserialize.dict_content_types(Dict[int, Optional[str]]), (int, Optional[str]))

        with self.assertRaises(TypeError):
            _ = deserialize.dict_content_types(int)

        with self.assertRaises(TypeError):
            _ = deserialize.dict_content_types(Tuple[List[int], int])


    def test_attribute_type_name(self):
        """Test attribute_type_name."""

        class CustomType:
            """Test type."""
            pass

        self.assertEqual(deserialize.attribute_type_name(Dict[int, int]), "Dict")
        self.assertEqual(deserialize.attribute_type_name(List[int]), "List")
        self.assertEqual(deserialize.attribute_type_name(Optional[str]), None)
        self.assertEqual(deserialize.attribute_type_name(Optional[List[str]]), None)
        self.assertEqual(deserialize.attribute_type_name(dict), None)
        self.assertEqual(deserialize.attribute_type_name(list), None)
        self.assertEqual(deserialize.attribute_type_name(str), None)
        self.assertEqual(deserialize.attribute_type_name(int), None)
        self.assertEqual(deserialize.attribute_type_name(CustomType), None)
