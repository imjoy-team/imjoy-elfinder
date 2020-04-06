#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""Assets for elfinder."""
from pyramid.config import Configurator


def includeme(config: Configurator) -> None:
    """Include templates and static assets in frontend."""
    config.include("pyramid_jinja2")
    config.add_jinja2_search_path("imjoy_elfinder:templates")
    config.add_static_view("static", "imjoy_elfinder:static")
