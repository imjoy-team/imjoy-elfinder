import os
import json
from setuptools import find_packages, setup

here = os.path.dirname(os.path.realpath(__file__))


def read(name):
    with open(os.path.join(here, name)) as f:
        return f.read()


with open(os.path.join(here, "jupyter_elfinder", "VERSION"), "r") as f:
    VERSION = json.load(f)["version"]

setup(
    name="jupyter-elfinder",
    version=VERSION,
    url="https://github.com/oeway/jupyter-elfinder",
    author="Wei OUYANG",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="nose.collector",
    license="MIT",
    description="A pyramid connector elfinder, specifically for working with jupyter server proxy.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    install_requires=read("requirements.txt"),
    tests_require=read("requirements.txt") + read("requirements-test.txt"),
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
    entry_points={
        "console_scripts": ["jupyter-elfinder = jupyter_elfinder.__main__:main"],
        "jupyter_serverproxy_servers": [
            "elfinder = jupyter_elfinder.__main__:setup_for_jupyter_server_proxy"
        ],
    },
)
