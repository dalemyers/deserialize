Custom Keys
-----------

It may be that you want to name your properties in your object something different to what is in the data. This can be for readability reasons, or because you have to (such as if your data item is named `__class__`). This can be handled too. Simply use the `key` annotation as follows:
::

    @deserialize.key("identifier", "id")
    class MyClass:
        value: int
        identifier: str

This will now assign the data with the key `id` to the field `identifier`. You can have multiple annotations to override multiple keys.
