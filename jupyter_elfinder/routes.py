#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Routes of elfinder
"""
from . import JUPYTER_ELFINDER_CONNECTOR, JUPYTER_ELFINDER_FILEBROWSER


def includeme(config):
    config.add_route(JUPYTER_ELFINDER_CONNECTOR, "/jupyter_elfinder/connector/")
    config.add_route(JUPYTER_ELFINDER_FILEBROWSER, "/jupyter_elfinder/filebrowser/")
