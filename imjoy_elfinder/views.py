#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""Provide views for elfinder."""
import json
import os
from cgi import FieldStorage

from pyramid.request import Request
from pyramid.response import Response, FileIter
from pyramid.view import view_config

from . import IMJOY_ELFINDER_CONNECTOR, IMJOY_ELFINDER_FILEBROWSER, elfinder
from .api_const import API_NAME, API_TARGETS, API_UPLOAD
from .util import get_all, get_one


def make_response(filename: str) -> Response:
    """Return a response."""
    res = Response(conditional_response=True)
    res.app_iter = FileIter(open(filename, "rb"), block_size=32768)
    res.content_length = os.path.getsize(filename)
    res.last_modified = os.path.getmtime(filename)
    res.etag = "%s-%s-%s" % (
        os.path.getmtime(filename),
        os.path.getsize(filename),
        hash(filename),
    )
    return res


@view_config(
    request_method=("GET", "POST", "OPTIONS"),
    route_name=IMJOY_ELFINDER_CONNECTOR,
    permission=IMJOY_ELFINDER_CONNECTOR,
)
def connector(request: Request) -> Response:
    """Handle the connector request."""
    # init connector and pass options
    root = request.registry.settings["root_dir"]
    options = {
        "root": os.path.abspath(root),
        "url": request.registry.settings["files_url"],
        "base_url": request.registry.settings["base_url"],
        "upload_max_size": 100 * 1024 * 1024 * 1024,  # 100GB
        "tmb_dir": request.registry.settings["thumbnail_dir"],
        "expose_real_path": request.registry.settings["expose_real_path"],
        "dot_files": request.registry.settings["dot_files"],
        "debug": True,
    }
    elf = elfinder.Connector(**options)

    # fetch only needed GET/POST parameters
    http_request = {}
    form = request.params
    for field in elf.http_allowed_parameters:
        if field in form:
            # Russian file names hack
            if field == API_NAME:
                http_request[field] = get_one(form, field).encode("utf-8")

            elif field == API_TARGETS:
                http_request[field] = get_all(form, field)

            # handle CGI upload
            elif field == API_UPLOAD:
                up_files = {}
                cgi_upload_files = get_all(form, field)
                for up_ in cgi_upload_files:
                    if isinstance(up_, FieldStorage) and up_.filename:
                        # pack dict(filename: filedescriptor)
                        up_files[up_.filename.encode("utf-8")] = up_.file
                http_request[field] = up_files
            else:
                http_request[field] = get_one(form, field)

    # run connector with parameters
    status, header, response = elf.run(http_request)

    if status == 200 and "__send_file" in response:
        # send file
        file_path = response["__send_file"]
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            result = make_response(file_path)
            result.headers.update(header)
            return result

        result = Response("Unable to find: {}".format(request.path_info))
    else:
        # get connector output and print it out
        result = Response(status=status)
        try:
            del header["Connection"]
        except KeyError:
            pass
        result.headers = header
        result.charset = "utf8"
        if "__text" in response:
            # output text
            result.text = response["__text"]
        else:
            # output json
            result.text = json.dumps(response)
    return result


@view_config(
    request_method="GET",
    route_name=IMJOY_ELFINDER_FILEBROWSER,
    permission=IMJOY_ELFINDER_FILEBROWSER,
    renderer="templates/elfinder/filebrowser.jinja2",
)
def index(request: Request) -> dict:
    """Handle the index request."""
    return {}
