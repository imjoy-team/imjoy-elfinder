"""Provide a main module."""
import os
import sys
import argparse
import json

from pyramid.config import Configurator
from jupyter_elfinder import JUPYTER_ELFINDER_FILEBROWSER, JUPYTER_ELFINDER_CONNECTOR
from pyramid.events import NewRequest
from pyramid.events import BeforeRender


def build_app(opt, **settings):
    """Build the app."""
    config = Configurator(settings=settings)
    config.include("jupyter_elfinder")

    # serve the folder content as static files under /static
    config.add_static_view("static", settings["jupyter_elfinder_root"])

    # serve the file browser under /
    config.add_route(JUPYTER_ELFINDER_FILEBROWSER, "/")

    def add_cors_headers_response_callback(event):
        def cors_headers(request, response):
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

    def add_global_params(event):
        """Add global parameters."""
        event["JUPYTER_ELFINDER_BASE_URL"] = settings["jupyter_base_url"]
        with open(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "VERSION"), "r"
        ) as f:
            version = json.load(f)["version"]
        event["JUPYTER_ELFINDER_VERSION"] = version

    config.add_subscriber(add_global_params, BeforeRender)

    return config.make_wsgi_app()


def main(args=None):
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
        default=None,
        help="The base url for accessing the file browser",
    )
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="host for the server"
    )
    parser.add_argument("--port", type=int, default=8765, help="port for the server")
    parser.add_argument(
        "--thumbnail", action="store_true", help="enable thumbnail for files"
    )

    opt = parser.parse_args(args=args)
    settings = {
        "jupyter_elfinder_root": opt.root_dir or os.getcwd(),
        "jupyter_elfinder_url": "/static",
        "jupyter_base_url": opt.base_url or "",
        "jupyter_elfinder_thumbnail_dir": ".tmb" if opt.thumbnail else None,
    }

    app = build_app(opt, **settings)

    from wsgiref.simple_server import make_server

    httpd = make_server(opt.host, opt.port, app)

    if opt.base_url and opt.base_url.startswith("http"):
        url = opt.base_url
    else:
        url = "http://{}:{}".format(opt.host, opt.port)

    print("==========Jupyter elFinder server is running=========\n{}\n".format(url))

    sys.stdout.flush()
    httpd.serve_forever()


def setup_for_jupyter_server_proxy():
    """Set up jupyter server proxy."""
    return {
        "command": [
            "jupyter-elfinder",
            "--port",
            "{port}",
            "--base-url",
            "{base_url}/proxy/{port}",
            "--allow-origin",
            "https://lib.imjoy.io",
        ]
    }


if __name__ == "__main__":
    main()
