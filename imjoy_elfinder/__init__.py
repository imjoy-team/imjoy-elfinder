"""
A pyramid connector elfinder, specifically for working with jupyter server proxy.

original file
https://github.com/Studio-42/elfinder-python/blob/master/connector.py changed
by Alexandr Rakov 08-03-2012
"""
from pyramid.config import Configurator
from elfinder_client import get_base_dir

IMJOY_ELFINDER_CONNECTOR = "imjoy_elfinder_connector"
IMJOY_ELFINDER_FILEBROWSER = "imjoy_elfinder_filebrowser"


def includeme(config: Configurator) -> None:
    """Include routes and assets."""
    # routes
    config.add_route(IMJOY_ELFINDER_FILEBROWSER, "/")
    config.add_route(IMJOY_ELFINDER_CONNECTOR, "/connector/")
    config.scan(".views")
    # assets
    config.include("pyramid_jinja2")
    config.add_jinja2_search_path("imjoy_elfinder:templates")
    config.add_static_view(name="static", path=get_base_dir())
