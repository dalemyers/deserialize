Default Values
--------

Some data will come to you with fields missing. In these cases, a default is often known. To do this, simply decorate your class like this:
::

    @deserialize.default("value", 0)
    class IntResult:
        successful: bool
        value: int

If you pass in data like `{"successful": True}` this will deserialize to a default value of `0` for `value`. Note, that this would not deserialize since `value` is not optional: `{"successful": True, "value": None}`.

Post-processing
---------------

Not everything can be set on your data straight away. Some things need to be figured out afterwards. For this you need to do some post-processing. The easiest way to do this is through the `@constructed` decorator. This decorator takes a function which will be called whenever a new instance is constructed with that instance as an argument. Here's an example which converts polar coordinates from using degrees to radians:
::

    data = {
        "angle": 180.0,
        "magnitude": 42.0
    }

    def convert_to_radians(instance):
        instance.angle = instance.angle * math.pi / 180

    @deserialize.constructed(convert_to_radians)
    class PolarCoordinate:
        angle: float
        magnitude: float

    pc = deserialize.deserialize(PolarCoordinate, data)

    print(pc.angle, pc.magnitude)

    >>> 3.141592653589793 42.0


Downcasting
-----------

Data often comes in the form of having the type as a field in the data. This can be difficult to parse. For example:
::

    data = [
        {
            "data_type": "foo",
            "foo_prop": "Hello World",
        },
        {
            "data_type": "bar",
            "bar_prop": "Goodbye World",
        }
    ]


Since the fields differ between the two, there's no good way of parsing this data. You could use optional fields on some base class, try multiple deserializations until you find the right one, or do the deserialization based on a mapping you build of the `data_type` field. None of those solutions are elegant though, and all have issues if the types are nested. Instead, you can use the `downcast_field` and `downcast_identifier` decorators.

`downcast_field` is specified on a base class and gives the name of the field that contains the type information. `downcast_identifier` takes in a base class and an identifier (which should be one of the possible values of the `downcast_field` from the base class). Internally, when a class with a downcast field is detected, the field will be extacted, and a subclass with a matching identifier will be searched for. If no such class exists, an `UndefinedDowncastException` will be thrown.

Here's an example which would handle the above data:
::

    @deserialize.downcast_field("data_type")
    class MyBase:
        type_name: str


    @deserialize.downcast_identifier(MyBase, "foo")
    class Foo(MyBase):
        foo_prop: str


    @deserialize.downcast_identifier(MyBase, "bar")
    class Bar(MyBase):
        bar_prop: str


    result = deserialize.deserialize(List[MyBase], data)

Here, `result[0]` will be an instance of `Foo` and `result[1]` will be an instance of `Bar`.
