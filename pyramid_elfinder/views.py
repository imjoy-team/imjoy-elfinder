#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Views for elfinder
"""
import os
import json
from cgi import FieldStorage

import elfinder
from pyramid.events import BeforeRender, subscriber
from pyramid.response import Response
from pyramid.view import view_config

from . import PYRAMID_ELFINDER_CONNECTOR, PYRAMID_ELFINDER_FILEBROWSER

# connector opts
_opts = {
    # 'root' and url rewrite from ini file
    'root': '/tmp',
    'URL': 'http://localhost:6543/static/uploaded',
    # other options
    'debug': True,
    # if False: download files using connector, no direct urls to files
    'fileURL': True,
    # 'dirSize': True,
    # 'dotFiles': True,
    'fileMode': 666,
    'dirMode': 777,
    # 'uploadDeny': ['image', 'application'],
    # 'uploadAllow': ['image/png', 'image/jpeg'],
    # 'uploadOrder': ['deny', 'allow']
}


@subscriber(BeforeRender)
def add_global_params(event):
    event['PYRAMID_ELFINDER_CONNECTOR'] = PYRAMID_ELFINDER_CONNECTOR
    event['PYRAMID_ELFINDER_FILEBROWSER'] = PYRAMID_ELFINDER_FILEBROWSER


@view_config(
    request_method=('GET', 'POST'),
    route_name=PYRAMID_ELFINDER_CONNECTOR,
    permission=PYRAMID_ELFINDER_CONNECTOR
)
def connector(request):
    # init connector and pass options
    root = request.registry.settings['pyramid_elfinder_root']
    _opts['root'] = os.path.abspath(root)
    # _opts['root'] = root'
    _opts['URL'] = request.registry.settings['pyramid_elfinder_url']
    elf = elfinder.connector(_opts)

    # fetch only needed GET/POST parameters
    httpRequest = {}
    form = request.params
    for field in elf.httpAllowedParameters:
        if field in form:
            # Russian file names hack
            if field == 'name':
                httpRequest[field] = form.getone(field).encode('utf-8')

            elif field == 'targets[]':
                httpRequest[field] = form.getall(field)

            # handle CGI upload
            elif field == 'upload[]':
                upFiles = {}
                cgiUploadFiles = form.getall(field)
                for up in cgiUploadFiles:
                    if isinstance(up, FieldStorage):
                        # pack dict(filename: filedescriptor)
                        upFiles[up.filename.encode('utf-8')] = up.file
                httpRequest[field] = upFiles
            else:
                httpRequest[field] = form.getone(field)

    # run connector with parameters
    status, header, response = elf.run(httpRequest)

    # get connector output and print it out
    result = Response(status=status)
    try:
        del header['Connection']
    except Exception:
        pass
    result.headers = header

    if response is not None and status == 200:
        # send file
        if 'file' in response and hasattr(response['file'], 'read'):
            result.body = response['file'].read()
            response['file'].close()

        # output json
        else:
            result.body = json.dumps(response)
    return result


@view_config(
    request_method='GET',
    route_name=PYRAMID_ELFINDER_FILEBROWSER,
    permission=PYRAMID_ELFINDER_FILEBROWSER,
    renderer='templates/elfinder/filebrowser.jinja2'
)
def index(request):
    return {}
