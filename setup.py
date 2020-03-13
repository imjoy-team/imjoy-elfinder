import os

from setuptools import find_packages, setup

here = os.path.dirname(os.path.realpath(__file__))


def read(name):
    with open(os.path.join(here, name)) as f:
        return f.read()

setup(
    name='jupyter_elfinder',
    version='0.1.3',
    url='https://github.com/oeway/jupyter-elfinder',
    author='Wei OUYANG',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="nose.collector",
    license="MIT",
    description='A pyramid connector elfinder, sepcifically for working with jupyter server proxy.',
    long_description=read('README.md'),
    install_requires=read('requirements.txt'),
    tests_require=read('requirements.txt') + read('requirements-test.txt'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
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
    entry_points={"console_scripts": ["jupyter-elfinder = jupyter_elfinder.__main__:main"]}
)
