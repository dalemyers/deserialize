Ignored Keys
------------

You may want some properties in your object that aren't loaded from disk, but instead created some other way. To do this, use the `ignore` decorator. Here's an example:
::

    @deserialize.ignore("identifier")
    class MyClass:
        value: int
        identifier: str

When deserializing, the library will now ignore the `identifier` property.
