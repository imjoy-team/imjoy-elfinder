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
from pyramid.response import Response
from pyramid.view import view_config

from . import JUPYTER_ELFINDER_CONNECTOR, JUPYTER_ELFINDER_FILEBROWSER, elfinder


class FileIterator:
    """Represent a file iterator."""

    chunk_size = 32768

    def __init__(self, filename: str) -> None:
        """Set up the file iterator instance."""
        self.filename = filename
        self.fileobj = open(self.filename, "rb")

    def __iter__(self) -> "FileIterator":
        """Return the file iterator."""
        return self

    def __next__(self) -> bytes:
        """Return the next item."""
        chunk = self.fileobj.read(self.chunk_size)
        if not chunk:
            raise StopIteration
        return chunk


class FileIterable:
    """Represent a file iterable."""

    def __init__(self, filename: str) -> None:
        """Set up file iterable instance."""
        self.filename = filename

    def __iter__(self) -> FileIterator:
        """Return the file iterator."""
        return FileIterator(self.filename)


def make_response(filename: str) -> Response:
    """Return a response."""
    res = Response(conditional_response=True)
    res.app_iter = FileIterable(filename)
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
    route_name=JUPYTER_ELFINDER_CONNECTOR,
    permission=JUPYTER_ELFINDER_CONNECTOR,
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
        "debug": True,
        "tmb_dir": request.registry.settings.get("jupyter_elfinder_thumbnail_dir"),
    }
    elf = elfinder.Connector(**options)

    # fetch only needed GET/POST parameters
    http_request = {}
    form = request.params
    for field in elf.http_allowed_parameters:
        if field in form:
            # Russian file names hack
            if field == "name":
                http_request[field] = form.getone(field).encode("utf-8")

            elif field == "targets[]":
                http_request[field] = form.getall(field)

            # handle CGI upload
            elif field == "upload[]":
                up_files = {}
                cgi_upload_files = form.getall(field)
                for up_ in cgi_upload_files:
                    if isinstance(up_, FieldStorage) and up_.filename:
                        # pack dict(filename: filedescriptor)
                        up_files[up_.filename.encode("utf-8")] = up_.file
                http_request[field] = up_files
            else:
                http_request[field] = form.getone(field)

    # run connector with parameters
    status, header, response = elf.run(http_request)

    if status == 200 and "file" in response:
        # send file
            file_path = response["file"]
            if os.path.exists(file_path) and not os.path.isdir(file_path):
                result = make_response(file_path)
                result.headers["Content-Length"] = elf.http_header["Content-Length"]
                result.headers["Content-type"] = elf.http_header["Content-type"]
                result.headers["Content-Disposition"] = elf.http_header[
                    "Content-Disposition"
                ]
                return result

            result = Response("Unable to find: {}".format(request.path_info))
        # output json
        else:
            # get connector output and print it out
            result = Response(status=status)
            try:
                del header["Connection"]
            except KeyError:
                pass
            result.headers = header
            result.charset = "utf8"
            result.text = json.dumps(response)
    return result


@view_config(
    request_method="GET",
    route_name=JUPYTER_ELFINDER_FILEBROWSER,
    permission=JUPYTER_ELFINDER_FILEBROWSER,
    renderer="templates/elfinder/filebrowser.jinja2",
)
def index(request: Request) -> dict:
    """Handle the index request."""
    return {}
