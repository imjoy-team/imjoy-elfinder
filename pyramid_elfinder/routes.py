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
from . import PYRAMID_ELFINDER_CONNECTOR, PYRAMID_ELFINDER_FILEBROWSER


def includeme(config):
    config.add_route(PYRAMID_ELFINDER_CONNECTOR,
                     '/pyramid_elfinder/connector/')
    config.add_route(PYRAMID_ELFINDER_FILEBROWSER,
                     '/pyramid_elfinder/filebrowser/')
