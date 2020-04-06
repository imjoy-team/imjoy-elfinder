"""Set up the imjoy_elfinder package."""
import json
import os

from setuptools import find_packages, setup

DESCRIPTION = (
    "A pyramid connector elfinder, specifically for working with jupyter server proxy."
)
HERE = os.path.dirname(os.path.realpath(__file__))


def read(name):
    """Read file name contents and return it."""
    with open(os.path.join(HERE, name)) as fil:
        return fil.read()


with open(os.path.join(HERE, "imjoy_elfinder", "VERSION"), "r") as f:
    VERSION = json.load(f)["version"]

setup(
    name="imjoy-elfinder",
    version=VERSION,
    url="https://github.com/oeway/imjoy-elfinder",
    author="ImJoy-Team",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    license="MIT",
    description=DESCRIPTION,
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    python_requires=">=3.5",
    install_requires=read("requirements.txt"),
    tests_require=read("requirements.txt") + read("requirements_test.txt"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Framework :: Pyramid ",
        "Topic :: Internet",
    ],
    extras_require={"jupyter": ["jupyter-server-proxy"]},
    entry_points={
        "console_scripts": ["imjoy-elfinder = imjoy_elfinder.__main__:main"],
        "jupyter_serverproxy_servers": [
            "elfinder = imjoy_elfinder.__main__:setup_for_jupyter_server_proxy"
        ],
    },
)
