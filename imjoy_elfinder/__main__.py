"""Provide a main module."""
import argparse
import json
import os
import sys
from socketserver import ThreadingMixIn
from typing import Any, Dict, List, Optional
from wsgiref.simple_server import WSGIServer, make_server

from pyramid.config import Configurator
from pyramid.events import BeforeRender, NewRequest
from pyramid.request import Request
from pyramid.response import Response
from pyramid.router import Router

from imjoy_elfinder import IMJOY_ELFINDER_FILEBROWSER


def build_app(opt: argparse.Namespace, settings: Dict[str, Optional[str]]) -> Router:
    """Build the app."""
    config = Configurator(settings=settings)
    config.include("imjoy_elfinder")

    # serve the folder content as static files under /static
    config.add_static_view(settings["files_url"], settings["root_dir"])

    # serve the file browser under /
    config.add_route(IMJOY_ELFINDER_FILEBROWSER, "/")

    def add_cors_headers_response_callback(event: Any) -> None:
        def cors_headers(request: Request, response: Response) -> None:
            response.headers.update(
                {
                    "Access-Control-Allow-Origin": opt.allow_origin,
                    "Access-Control-Allow-Methods": "POST,GET,DELETE,PUT,OPTIONS",
                    "Access-Control-Allow-Headers": (
                        "Origin, Content-Type, Accept, Authorization, x-requested-with"
                    ),
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Max-Age": "1728000",
                }
            )

        event.request.add_response_callback(cors_headers)

    # add cors headers
    config.add_subscriber(add_cors_headers_response_callback, NewRequest)

    def add_global_params(event: Any) -> None:
        """Add global parameters."""
        event["IMJOY_ELFINDER_BASE_URL"] = settings["base_url"]
        with open(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "VERSION"), "r"
        ) as fil:
            version = json.load(fil)["version"]
        event["IMJOY_ELFINDER_VERSION"] = version

    config.add_subscriber(add_global_params, BeforeRender)

    return config.make_wsgi_app()


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    """Represent a threading WSGI server."""


def main(args: Optional[List[str]] = None) -> None:
    """Run the app."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root-dir",
        type=str,
        default=None,
        help="The root folder for the file browser.",
    )
    parser.add_argument(
        "--allow-origin",
        type=str,
        default="",
        help="The Access-Control-Allow-Origin header, by default it's empty.",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="",
        help="The base url for accessing the file browser",
    )
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="host for the server"
    )
    parser.add_argument("--port", type=int, default=8765, help="port for the server")
    parser.add_argument(
        "--thumbnail", action="store_true", help="enable thumbnail for files"
    )
    parser.add_argument(
        "--dot-files", action="store_true", help="show dotfiles or folders"
    )
    parser.add_argument(
        "--expose-real-path",
        action="store_true",
        help="send file path to the frontend (disabled for security reason)",
    )

    opt = parser.parse_args(args=args)

    # normalize base url, this is needed to fix
    # duplicated slash from jupyter server proxy
    if opt.base_url.startswith("http"):
        tmp = opt.base_url.split("://")
        tmp[1] = tmp[1].replace("//", "/")
        opt.base_url = "://".join(tmp)
    else:
        opt.base_url = opt.base_url.replace("//", "/")

    settings = {
        "root_dir": opt.root_dir or os.getcwd(),
        "files_url": "/files",
        "base_url": opt.base_url,
        "expose_real_path": opt.expose_real_path,
        "thumbnail_dir": ".tmb" if opt.thumbnail else None,
        "dot_files": opt.dot_files,
    }  # type: Dict[str, Optional[str]]

    app = build_app(opt, settings)

    httpd = make_server(opt.host, opt.port, app, ThreadingWSGIServer)

    if opt.base_url and opt.base_url.startswith("http"):
        url = opt.base_url
    else:
        url = "http://{}:{}".format(opt.host, opt.port)

    print("==========ImJoy elFinder server is running=========\n{}\n".format(url))

    sys.stdout.flush()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nClosing server")
        httpd.server_close()


def setup_for_jupyter_server_proxy() -> dict:
    """Set up jupyter server proxy."""

    return {
        "command": [
            "imjoy-elfinder",
            "--port",
            "{port}",
            "--base-url",
            "{base_url}/elfinder",
            "--allow-origin",
            "https://lib.imjoy.io",
            "--thumbnail",
            "--expose-real-path",
        ],
        "environment": {},
        "launcher_entry": {
            "title": "ImJoy elFinder",
            "icon_path": os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "static", "img", "icon.png"
            ),
        },
    }


if __name__ == "__main__":
    main()
