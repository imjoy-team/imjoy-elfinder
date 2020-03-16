#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""Provide routes of elfinder."""
from . import JUPYTER_ELFINDER_CONNECTOR, JUPYTER_ELFINDER_FILEBROWSER


def includeme(config):
    """Include routes in frontend."""
    config.add_route(JUPYTER_ELFINDER_CONNECTOR, "/connector/")
