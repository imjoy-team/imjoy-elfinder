#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Mixin for elfinder field
"""
from sqlalchemy.types import TypeDecorator, Unicode


class ElfinderString(TypeDecorator):
    impl = Unicode

    def __init__(self, *arg, **kw):
        TypeDecorator.__init__(self, *arg, **kw)

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return value
