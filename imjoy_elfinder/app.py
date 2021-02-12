"""Provide the app module."""
import argparse
from dotenv import load_dotenv, find_dotenv
import json
import os
import sys

from typing import Any, Dict, List, Optional
from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from imjoy_elfinder import __version__
from .settings import get_settings
from imjoy_elfinder import views

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


def build_app(settings) -> FastAPI:
    app = FastAPI(
        title="ImJoy AI Server",
        description="A backend server for managing files, tasks, models for AI applications",
        version=__version__,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://lib.imjoy.io", "https://imjoy.io"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["Content-Type", "Authorization"],
    )

    from elfinder_client import get_base_dir

    app.mount("/static", StaticFiles(directory=get_base_dir()), name="static")
    app.include_router(views.router)

    return app


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
    parser.add_argument("--dev", action="store_true", help="enable development mode")

    opt = parser.parse_args(args=args)

    # normalize base url, this is needed to fix
    # duplicated slash from jupyter server proxy
    if opt.base_url.startswith("http"):
        tmp = opt.base_url.split("://")
        tmp[1] = tmp[1].replace("//", "/")
        opt.base_url = "://".join(tmp)
    else:
        opt.base_url = opt.base_url.replace("//", "/")

    settings = get_settings()

    settings.root_dir = opt.root_dir or os.getcwd()
    settings.files_url = "/files"
    settings.base_url = opt.base_url
    settings.expose_real_path = opt.expose_real_path
    settings.thumbnail_dir = ".tmb" if opt.thumbnail else None
    settings.dot_files = opt.dot_files

    app = build_app(settings)
    if opt.base_url and opt.base_url.startswith("http"):
        url = opt.base_url
    else:
        url = "http://{}:{}".format(opt.host, opt.port)

    print("==========ImJoy elFinder server is running=========\n{}\n".format(url))

    sys.stdout.flush()

    try:
        uvicorn.run(app, host=opt.host, port=opt.port, log_level="info")
    except KeyboardInterrupt:
        print("\nClosing server")


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
