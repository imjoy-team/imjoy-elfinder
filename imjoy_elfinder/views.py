#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""Provide views for elfinder."""
import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
)
from fastapi.templating import Jinja2Templates
from starlette.datastructures import FormData

from . import __version__, elfinder
from .api_const import API_DIRS, API_NAME, API_TARGETS, API_UPLOAD, API_UPLOAD_PATH
from .util import get_all, get_form_body, get_one

router = APIRouter()

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("/connector")
@router.post("/connector")
@router.options("/connector")
def connector(
    request: Request, request_body: FormData = Depends(get_form_body)
) -> Response:
    """Handle the connector request."""
    # init connector and pass options
    settings = request.app.state.settings
    root = settings.root_dir
    options = {
        "root": os.path.abspath(root),
        "url": settings.files_url,
        "base_url": settings.base_url,
        "upload_max_size": 100 * 1024 * 1024 * 1024,  # 100GB
        "tmb_dir": settings.thumbnail_dir,
        "expose_real_path": settings.expose_real_path,
        "dot_files": settings.dot_files,
        "debug": True,
    }
    elf = elfinder.Connector(**options)
    # fetch only needed GET/POST parameters
    http_request = {}
    query_params = request.query_params
    for field in elf.http_allowed_parameters:
        if field in request_body:
            # handle CGI upload
            if field == API_UPLOAD:
                http_request[field] = get_all(request_body, field)
            elif field == API_UPLOAD_PATH:
                http_request[field] = get_all(request_body, field)
            else:
                http_request[field] = get_one(request_body, field)
        elif field in query_params:
            # Russian file names hack
            if field == API_NAME:
                http_request[field] = get_one(query_params, field).encode("utf-8")

            elif field == API_TARGETS:
                http_request[field] = get_all(query_params, field)

            elif field == API_DIRS:
                http_request[field] = get_all(query_params, field)

            else:
                http_request[field] = get_one(query_params, field)

    # run connector with parameters
    status, header, response = elf.run(http_request)
    if status == 200 and "__send_file" in response:
        # send file
        file_path = response["__send_file"]
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            return FileResponse(file_path, headers=header)

        return PlainTextResponse(f"Unable to find: {request.url}", headers=header)

    # get connector output and print it out
    if "__text" in response:
        # output text
        result = PlainTextResponse(response["__text"], headers=header)
    else:
        # output json
        result = JSONResponse(response, headers=header)

    result.status_code = status
    try:
        del header["Connection"]
    except KeyError:
        pass

    result.charset = "utf8"
    return result


@router.get("/", response_class=HTMLResponse)
@router.get("/filebrowser", response_class=HTMLResponse)
def index(request: Request) -> Response:
    """Handle the index request."""
    return templates.TemplateResponse(
        "elfinder/filebrowser.jinja2",
        {"request": request, "IMJOY_ELFINDER_VERSION": __version__},
    )
