"""Handlers for case conversions for strings."""


def camel_case(string):
    """Convert a string to camel case from snake case."""
    string = pascal_case(string)
    if len(string) > 1:
        string = string[0].lower() + string[1:]
    else:
        string = string.lower()
    return string


def pascal_case(string):
    """Convert a string to pascal case from snake case."""
    string = string.title()
    string = string.replace("_", "")
    return string
