#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Assets for elfinder
"""


def includeme(config):
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("jupyter_elfinder:templates")
    config.add_static_view('jupyter_elfinder_static',
                           'jupyter_elfinder:static')