
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
