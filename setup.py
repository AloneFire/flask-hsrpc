# -*- coding: utf-8 -*-
import re
import setuptools


def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version


__version__ = find_version('flask_hsrpc/__version__.py')


setuptools.setup(
    name="flask-hsrpc",
    version=__version__,
    url="https://github.com/AloneFire/flask-hsrpc.git",

    author="alonefire",
    author_email="alonefire@foxmail.com",

    description="flask hsrpc plugin",
    long_description='flask hsrpc plugin',

    packages=setuptools.find_packages(),

    install_requires=[
        "Flask>=1.0.2",
        "marshmallow>=2.15.1",
        "python-consul>=0.7.2",
        "requests>=2.18.4"
    ],

    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
)
