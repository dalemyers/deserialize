Default Values
--------

Some data will come to you with fields missing. In these cases, a default is often known. To do this, simply decorate your class like this:
::

    @deserialize.default("value", 0)
    class IntResult:
        successful: bool
        value: int

If you pass in data like `{"successful": True}` this will deserialize to a default value of `0` for `value`. Note, that this would not deserialize since `value` is not optional: `{"successful": True, "value": None}`.
