"""Provide request validation."""
from typing import Any

import voluptuous as vol


def string(value: Any) -> str:
    """Validate that value is a non empty string."""
    if not isinstance(value, str):
        raise vol.Invalid("Value is {} not a string.".format(value))
    if not value:
        raise vol.Invalid("Value {} is an empty string.".format(value))
    return value
