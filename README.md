# deserialize

A library to make deserialization easy.

Without the library, if you want to convert:

```
{
    "a": 1,
    "b": 2
}
```

into a dedicated class, you had to do something like this:

```
class MyThing:

    def __init__(self, a, b):
        self.a = a
        self.b = b

    @staticmethod
    def from_json(json_data):
        a_value = json_data.get("a")
        b_value = json_data.get("b")

        if a_value is None:
            raise Exception("'a' was None")
        elif b_value is None:
            raise Exception("'b' was None")
        elif type(a_value) != int:
            raise Exception("'a' was not an int")
        elif type(b_value) != int:
            raise Exception("'b' was not an int")

        return MyThing(a_value, b_value)

my_instance = MyThing.from_json(json_data)
```

With `deserialize` all you need to do is this:

```
import deserialize

class MyThing:
    a: int
    b: int

my_instance = deserialize.deserialize(MyThing, json_data)
```

That's it. It will pull out all the data and set it for you type checking and even checking for null values.

If you want null values to be allowed though, that's easy too:

```
from typing import Optional

class MyThing:
    a: Optional[int]
    b: Optional[int]
```

Now `None` is a valid value for these.

Types can be nested as deep as you like. For example, this is perfectly valid:

```
class Actor:
    name: str
    age: int

class Episode:
    title: str
    identifier: st
    actors: List[Actor]

class Season:
    episodes: List[Episode]
    completed: bool

class TVShow:
    seasons: List[Season]
    creator: str
```
