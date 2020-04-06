#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""Provide routes of elfinder."""
from pyramid.config import Configurator

from . import IMJOY_ELFINDER_CONNECTOR


def includeme(config: Configurator) -> None:
    """Include routes in frontend."""
    config.add_route(IMJOY_ELFINDER_CONNECTOR, "/connector/")
