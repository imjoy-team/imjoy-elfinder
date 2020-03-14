"""Set up the jupyter_elfinder package."""
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


with open(os.path.join(HERE, "jupyter_elfinder", "VERSION"), "r") as f:
    VERSION = json.load(f)["version"]

setup(
    name="jupyter-elfinder",
    version=VERSION,
    url="https://github.com/oeway/jupyter-elfinder",
    author="Wei OUYANG",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    license="MIT",
    description=DESCRIPTION,
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    install_requires=read("requirements.txt"),
    tests_require=read("requirements.txt") + read("requirements_test.txt"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Framework :: Pyramid ",
        "Topic :: Internet",
    ],
    extras_require={"jupyter": ["jupyter-server-proxy"]},
    entry_points={
        "console_scripts": ["jupyter-elfinder = jupyter_elfinder.__main__:main"],
        "jupyter_serverproxy_servers": [
            "elfinder = jupyter_elfinder.__main__:setup_for_jupyter_server_proxy"
        ],
    },
)
