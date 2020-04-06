"""Provide utils."""
from typing import Any, List

from pyramid.interfaces import IMultiDict


def get_one(multi_dict: IMultiDict, key: str) -> Any:
    """Return one value matching the key in the dict.

    Raise KeyError if multiple values were found.
    """
    matched = [v for k, v in multi_dict.items() if k == key]
    if len(matched) > 1:
        raise KeyError("{} matched more than one key in {}".format(key, multi_dict))
    return next(iter(matched), None)


def get_all(multi_dict: IMultiDict, key: str) -> List[Any]:
    """Return a list with all values matching the key in the dict.

    May return an empty list.
    """
    matched = [v for k, v in multi_dict.items() if k == key]
    return matched
