"""Test deserializing."""

import datetime
import os
import sys
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from deserialize import deserialize, parser

# pylint: enable=wrong-import-position


@parser("int_field", int)
@parser("datetime_field", datetime.datetime.fromtimestamp)
@parser("some_values", lambda x: [y * 2 for y in x])
class SampleItem:
    """Sample item for use in tests."""

    int_field: int
    datetime_field: datetime.datetime
    some_values: List[int]


def test_parser() -> None:
    """Test that parsers are applied correctly."""

    instance = deserialize(
        SampleItem,
        {"int_field": "1", "datetime_field": 1543770752, "some_values": [1, 2, 3]},
    )
    assert instance.int_field == 1
    assert instance.datetime_field == datetime.datetime(2018, 12, 2, 17, 12, 32)
    assert instance.some_values == [2, 4, 6]
