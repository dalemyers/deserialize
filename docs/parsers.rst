Parsers
-------

Sometimes you'll want something in your object in a format that the data isn't in. For example, if you get the data:
::

    {
        "successful": True,
        "timestamp": 1543770752
    }

You may want that to be represented as:
::

    class Result:
        successful: bool
        timestamp: datetime.datetime

By default, it will fail on this deserialization as the value in the data is not a timestamp. To correct this, use the `parser` decorator to tell it a function to use to parse the data. E.g.
::

    @deserialize.parser("timestamp", datetime.datetime.fromtimestamp)
    class Result:
        successful: bool
        timestamp: datetime.datetime

This will now detect when handling the data for the _key_ `timestamp` and run it through the parser function supplied before assigning it to your new class instance.

The parser is run _before_ type checking is done. This means that if you had something like `Optional[datetime.datetime]`, you should ensure your parser can handle the value being `None`. Your parser will obviously need to return the type that you have declared on the property in order to work.
