"""Provide a main module."""
import os
import sys
import argparse

from pyramid.config import Configurator
from jupyter_elfinder import JUPYTER_ELFINDER_FILEBROWSER
from pyramid.events import NewRequest


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
                    "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, x-requested-with",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Max-Age": "1728000",
                }
            )

        event.request.add_response_callback(cors_headers)

    # add cors headers
    config.add_subscriber(add_cors_headers_response_callback, NewRequest)
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

    here = os.path.dirname(os.path.realpath(__file__))
    example_data = os.path.join(here, "..", "example-data")

    settings = {
        "jupyter_elfinder_root": opt.root_dir or example_data,
        "jupyter_elfinder_url": "/static",
        "jupyter_base_url": opt.base_url or "",
        "jupyter_elfinder_thumbnail_dir": ".tmb" if opt.thumbnail else None,
    }

    app = build_app(opt, **settings)

    from wsgiref.simple_server import make_server

    httpd = make_server(opt.host, opt.port, app)
    print(
        "==========Jupyter elFinder server is running=========\nhttp://{}:{}\n".format(
            opt.host, opt.port
        )
    )
    sys.stdout.flush()
    httpd.serve_forever()


def setup_for_jupyter_server_proxy():
    """Set up jupyter server proxy."""
    return {
        "command": ["jupyter-elfinder", "--port", "{port}", "--base-url", "{base_url}"]
    }


if __name__ == "__main__":
    main()
