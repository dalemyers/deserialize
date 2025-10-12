![Code scanning - action](https://github.com/dalemyers/deserialize/workflows/Code%20scanning%20-%20action/badge.svg) [![PyPI version](https://badge.fury.io/py/deserialize.svg)](https://badge.fury.io/py/deserialize) ![Azure DevOps builds](https://img.shields.io/azure-devops/build/dalemyers/Github/3)

# deserialize

A library to make deserialization easy. To get started, just run `pip install deserialize`

### How it used to be

Without the library, if you want to convert:

```json
{
    "a": 1,
    "b": 2
}
```

into a dedicated class, you had to do something like this:

```python
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

### How it is now

With `deserialize` all you need to do is this:

```python
import deserialize

class MyThing:
    a: int
    b: int

my_instance = deserialize.deserialize(MyThing, json_data)
```

That's it. It will pull out all the data and set it for you type checking and even checking for null values.

If you want null values to be allowed though, that's easy too:

```python
class MyThing:
    a: int | None
    b: int | None
```

Now `None` is a valid value for these.

Types can be nested as deep as you like. For example, this is perfectly valid:

```python
class Actor:
    name: str
    age: int

class Episode:
    title: str
    identifier: str
    actors: list[Actor]

class Season:
    episodes: list[Episode]
    completed: bool

class TVShow:
    seasons: list[Season]
    creator: str
```

## Advanced Usage

### Field Configuration with Annotated

You can use `Field` with `Annotated` type hints to configure field behavior. This is the **recommended approach** as it provides a modern, Pythonic API that's familiar to users of libraries like Pydantic and FastAPI.

```python
from deserialize import Annotated, deserialize, Field

class User:
    user_id: Annotated[int, Field(alias="userId")]
    email: Annotated[str, Field(alias="emailAddress")]
    is_active: Annotated[bool, Field(default=True)]

data = {"userId": 123, "emailAddress": "user@example.com"}
user = deserialize(User, data)
# user.user_id = 123
# user.email = "user@example.com"  
# user.is_active = True (from default)
```

`Field` supports the following options:

- **`alias`**: Alternative key name in source data
  ```python
  user_id: Annotated[int, Field(alias="userId")]
  ```

- **`default`**: Default value if field is missing
  ```python
  is_active: Annotated[bool, Field(default=True)]
  ```

- **`parser`**: Function to transform the value before assignment
  ```python
  import datetime
  
  created_at: Annotated[datetime.datetime, Field(parser=datetime.datetime.fromtimestamp)]
  ```

- **`ignore`**: Skip this field during deserialization
  ```python
  internal_id: Annotated[str, Field(ignore=True)]
  ```

**Benefits of using Field:**
- Configuration is co-located with the field definition
- Better IDE autocomplete and type checking
- More familiar to users of modern Python libraries
- Easier to read - all field info in one place
- Type-safe and validated at the point of declaration

### Handling Different Key Names

Data often comes with keys that don't match Python naming conventions. Use `Field(alias=...)` to map between them:

```python
from deserialize import Annotated, Field

class MyClass:
    # Map 'id' in data to 'identifier' in Python
    identifier: Annotated[str, Field(alias="id")]
    value: int
```

For automatic camelCase/PascalCase to snake_case conversion, use the `auto_snake` decorator:

```python
from deserialize import Annotated, Field, auto_snake

@auto_snake()
class MyClass:
    some_integer: int
    some_string: str
    # Automatically maps "SomeInteger" and "SomeString" from data
```

### Unhandled Fields

Usually, if you don't specify a field in your definition but it exists in the data, it will be ignored. If you want to be notified about extra fields, set `throw_on_unhandled=True` when calling `deserialize(...)`:

```python
# Will raise an exception if data has fields not defined in MyClass
result = deserialize(MyClass, data, throw_on_unhandled=True)
```

To explicitly allow specific fields to be unhandled, use the `@allow_unhandled` decorator:

```python
@deserialize.allow_unhandled("metadata")
class MyClass:
    value: int
```

### Ignored Fields

Some properties in your class may not come from the deserialized data. Mark them as ignored using `Field(ignore=True)`:

```python
from deserialize import Annotated, Field

class MyClass:
    value: int
    # This field won't be deserialized
    identifier: Annotated[str, Field(ignore=True)]
```

### Value Transformation with Parsers

Transform values during deserialization using `Field(parser=...)`. This is useful when the data format doesn't match your desired type:

```python
from deserialize import Annotated, Field
import datetime

class Result:
    successful: bool
    # Convert Unix timestamp to datetime
    timestamp: Annotated[datetime.datetime, Field(parser=datetime.datetime.fromtimestamp)]

# Input: {"successful": True, "timestamp": 1543770752}
# result.timestamp will be a datetime object
```

The parser runs before type checking. If your field accepts `None`, ensure your parser handles it:

```python
def parse_timestamp(value):
    if value is None:
        return None
    return datetime.datetime.fromtimestamp(value)

class Result:
    timestamp: Annotated[datetime.datetime | None, Field(parser=parse_timestamp)]
```


### Subclassing

Subclassing is fully supported. Properties from parent classes are automatically included during deserialization:

```python
class Shape:
    color: str

class Rectangle(Shape):
    width: int
    height: int

# Will deserialize both 'color' and rectangle-specific fields
```

### Raw Data Storage

Keep a reference to the raw data used for construction by setting the `raw_storage_mode` parameter:

```python
from deserialize import deserialize, RawStorageMode

result = deserialize(MyClass, data, raw_storage_mode=RawStorageMode.ROOT)
# Access via: result.__deserialize_raw__
```

Options:
- `RawStorageMode.ROOT`: Store raw data only on the root object
- `RawStorageMode.ALL`: Store raw data on all objects in the tree

### Default Values

Provide default values for missing fields using `Field(default=...)`:

```python
from deserialize import Annotated, Field

class IntResult:
    successful: bool
    value: Annotated[int, Field(default=0)]

# Input: {"successful": True}
# result.value will be 0
```

Note: Defaults only apply when the field is missing from the data. If the field is present with value `None`, it will fail unless the type allows `None`.

### Post-processing

Not everything can be set on your data straight away. Some things need to be figured out afterwards. For this you need to do some post-processing. The easiest way to do this is through the `@constructed` decorator. This decorator takes a function which will be called whenever a new instance is constructed with that instance as an argument. Here's an example which converts polar coordinates from using degrees to radians:

```python
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
```


### Downcasting

Data often comes in the form of having the type as a field in the data. This can be difficult to parse. For example:

```python
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
```

Since the fields differ between the two, there's no good way of parsing this data. You could use optional fields on some base class, try multiple deserializations until you find the right one, or do the deserialization based on a mapping you build of the `data_type` field. None of those solutions are elegant though, and all have issues if the types are nested. Instead, you can use the `downcast_field` and `downcast_identifier` decorators.

`downcast_field` is specified on a base class and gives the name of the field that contains the type information. `downcast_identifier` takes in a base class and an identifier (which should be one of the possible values of the `downcast_field` from the base class). Internally, when a class with a downcast field is detected, the field will be extacted, and a subclass with a matching identifier will be searched for. If no such class exists, an `UndefinedDowncastException` will be thrown.

Here's an example which would handle the above data:

```python
@deserialize.downcast_field("data_type")
class MyBase:
    type_name: str


@deserialize.downcast_identifier(MyBase, "foo")
class Foo(MyBase):
    foo_prop: str


@deserialize.downcast_identifier(MyBase, "bar")
class Bar(MyBase):
    bar_prop: str


result = deserialize.deserialize(list[MyBase], data)
```

Here, `result[0]` will be an instance of `Foo` and `result[1]` will be an instance of `Bar`.

If you can't describe all of your types, you can use `@deserialize.allow_downcast_fallback` on your base class and any unknowns will be left as dictionaries.


### Custom Deserializing

If none of the above work for you, sometimes there's no choice but to turn to customized deserialization code. To do this is very easy. Simply implement the `CustomDeserializable` protocol, and add the `deserialize` method to your class like so:

```python
class MyObject(deserialize.CustomDeserializable):

    name: str
    age: int

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    @classmethod
    def deserialize(cls, value: Any) -> "MyObject":
        assert isinstance(value, list)
        assert len(value) == 2

        return cls(value[0], value[1])
```

Normally you'd use a dictionary to create an object (something like `{"name": "Hodor", "age": 42}`), but this now allows us to use a list. i.e. `my_instance = deserialize.deserialize(MyObject, ["Hodor", 42])`

No type checking is done on the result or input. It's entirely on the implementer at this point.

---

## Deprecated Features

The following decorator-based features are **deprecated** and maintained only for backward compatibility. New code should use `Field` with `Annotated` instead.

### Deprecated: @key decorator

**❌ Old way (deprecated):**
```python
@deserialize.key("identifier", "id")
class MyClass:
    identifier: str
```

**✅ New way:**
```python
from deserialize import Annotated, Field

class MyClass:
    identifier: Annotated[str, Field(alias="id")]
```

### Deprecated: @default decorator

**❌ Old way (deprecated):**
```python
@deserialize.default("value", 0)
class MyClass:
    value: int
```

**✅ New way:**
```python
from deserialize import Annotated, Field

class MyClass:
    value: Annotated[int, Field(default=0)]
```

### Deprecated: @parser decorator

**❌ Old way (deprecated):**
```python
@deserialize.parser("timestamp", datetime.datetime.fromtimestamp)
class Result:
    timestamp: datetime.datetime
```

**✅ New way:**
```python
from deserialize import Annotated, Field
import datetime

class Result:
    timestamp: Annotated[datetime.datetime, Field(parser=datetime.datetime.fromtimestamp)]
```

### Deprecated: @ignore decorator

**❌ Old way (deprecated):**
```python
@deserialize.ignore("identifier")
class MyClass:
    identifier: str
```

**✅ New way:**
```python
from deserialize import Annotated, Field

class MyClass:
    identifier: Annotated[str, Field(ignore=True)]
```

**Note:** If both `Field` and decorators are used for the same field, `Field` takes precedence.