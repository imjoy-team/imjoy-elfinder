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


def includeme(config):
    config.add_route('elfinder_connector', '/elfinder_connector')
    config.add_route('elfinder', '/elfinder/')
