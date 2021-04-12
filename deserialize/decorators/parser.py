"""Decorators used for adding functionality to the library."""

import inspect


def _generate_key(class_reference):
    """Generate a key for lookups."""
    return str(class_reference)


def set_property(class_reference, property_name, key_name, property_value):
    """A apply a property to a class."""

    if not hasattr(class_reference, property_name):
        setattr(class_reference, property_name, {})

    class_key = _generate_key(class_reference)

    subclass_map = getattr(class_reference, property_name, {}).get(class_key)

    if subclass_map is None:
        getattr(class_reference, property_name)[class_key] = {}

    getattr(class_reference, property_name)[class_key][key_name] = property_value


def _get_property(class_reference, property_name, key_name, sentinel_value):
    """Get the property for the given class, property and key name."""

    if not hasattr(class_reference, property_name):
        return sentinel_value

    class_key = class_key = _generate_key(class_reference)
    subclass_map = getattr(class_reference, property_name, {}).get(class_key)

    if subclass_map:
        value = subclass_map.get(key_name, sentinel_value)
        if value != sentinel_value:
            return value

    for superclass in inspect.getmro(class_reference):
        if superclass == class_reference:
            continue

        value = _get_property(superclass, property_name, key_name)
        if value != sentinel_value:
            return value

    return sentinel_value
