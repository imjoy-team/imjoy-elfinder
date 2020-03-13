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

from . import elfinder
from pyramid.view import view_config
from pyramid.events import subscriber, BeforeRender
from pyramid.response import Response, FileResponse

from . import PYRAMID_ELFINDER_CONNECTOR, PYRAMID_ELFINDER_FILEBROWSER

class FileIterable(object):
    def __init__(self, filename):
        self.filename = filename
    def __iter__(self):
        return FileIterator(self.filename)
class FileIterator(object):
    chunk_size = 32768
    def __init__(self, filename):
        self.filename = filename
        self.fileobj = open(self.filename, 'rb')
    def __iter__(self):
        return self
    def next(self):
        chunk = self.fileobj.read(self.chunk_size)
        if not chunk:
            raise StopIteration
        return chunk
    __next__ = next # py3 compat

def make_response(filename):
    res = Response(conditional_response=True)
    res.app_iter = FileIterable(filename)
    res.content_length = os.path.getsize(filename)
    res.last_modified = os.path.getmtime(filename)
    res.etag = '%s-%s-%s' % (os.path.getmtime(filename),
                             os.path.getsize(filename), hash(filename))
    return res

@subscriber(BeforeRender)
def add_global_params(event):
    event['PYRAMID_ELFINDER_CONNECTOR'] = PYRAMID_ELFINDER_CONNECTOR
    event['PYRAMID_ELFINDER_FILEBROWSER'] = PYRAMID_ELFINDER_FILEBROWSER


@view_config(
    request_method=('GET', 'POST', 'OPTIONS'),
    route_name=PYRAMID_ELFINDER_CONNECTOR,
    permission=PYRAMID_ELFINDER_CONNECTOR
)
def connector(request):
    # init connector and pass options
    root = request.registry.settings['pyramid_elfinder_root']
    options = {
        'root': os.path.abspath(root),
        'URL': '', # request.registry.settings['pyramid_elfinder_url'],
        'uploadMaxSize': 1024*1024, #MB
        'debug': True
    }
    elf = elfinder.connector(options)

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

    

    if response is not None and status == 200:
        # send file
        if 'file' in response:
            file_path = response['file']
            if os.path.exists(file_path) and not os.path.isdir(file_path):
                result = make_response(file_path)
                result.headers['Content-Length'] = elf.httpHeader['Content-Length']
                result.headers['Content-type'] = elf.httpHeader['Content-type']
                result.headers['Content-Disposition'] = elf.httpHeader['Content-Disposition']
                return result
            else:
                result = Response("Unable to find: {}".format(request.path_info))
        # output json
        else:
            # get connector output and print it out
            result = Response(status=status)
            try:
                del header['Connection']
            except Exception:
                pass
            result.headers = header
            result.charset = 'utf8'
            result.text = json.dumps(response)
    return result


@view_config(
    request_method='GET',
    route_name=PYRAMID_ELFINDER_FILEBROWSER,
    permission=PYRAMID_ELFINDER_FILEBROWSER,
    renderer='templates/elfinder/filebrowser.jinja2'
)
def index(request):
    return {}
