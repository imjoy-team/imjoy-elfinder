"""
A pyramid connector elfinder, specifically for working with jupyter server proxy.

original file
https://github.com/Studio-42/elfinder-python/blob/master/connector.py changed
by Alexandr Rakov 08-03-2012
"""
from pyramid.config import Configurator

IMJOY_ELFINDER_CONNECTOR = "imjoy_elfinder_connector"
IMJOY_ELFINDER_FILEBROWSER = "imjoy_elfinder_filebrowser"


def includeme(config: Configurator) -> None:
    """Include frontend."""
    config.include(".routes")
    config.include(".assets")
    config.scan(".views")
