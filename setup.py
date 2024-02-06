"""Set up the imjoy_elfinder package."""
import json
from pathlib import Path

from setuptools import find_packages, setup

DESCRIPTION = (
    "An elfinder connector built with FastAPI, "
    "specifically for working with jupyter server proxy."
)
ROOT_DIR = Path(__file__).parent.resolve()
README_FILE = ROOT_DIR / "README.md"
LONG_DESCRIPTION = README_FILE.read_text(encoding="utf-8")
VERSION_FILE = ROOT_DIR / "imjoy_elfinder" / "VERSION"
VERSION = json.loads(VERSION_FILE.read_text(encoding="utf-8"))["version"]

REQUIRES = [
    "aiofiles",
    "elfinder-client",
    "fastapi",
    "jinja2",
    "pathvalidate",
    "pillow",
    "python-dotenv",
    "python-multipart",
    "typing_extensions",
    "uvicorn[standard]",
    "pydantic<2,>=1.8.2",
]


setup(
    name="imjoy-elfinder",
    version=VERSION,
    url="https://github.com/imjoy-team/imjoy-elfinder",
    author="ImJoy-Team",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    license="MIT",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    install_requires=REQUIRES,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: FastAPI ",
        "Topic :: Internet",
    ],
    extras_require={"jupyter": ["jupyter-server-proxy"]},
    entry_points={
        "console_scripts": ["imjoy-elfinder = imjoy_elfinder.app:main"],
        "jupyter_serverproxy_servers": [
            "elfinder = imjoy_elfinder.app:setup_for_jupyter_server_proxy"
        ],
    },
)
