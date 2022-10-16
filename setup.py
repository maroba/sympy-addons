#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
from os.path import exists
from setuptools import setup, find_packages

author = 'Matthias Baer'
email = 'matthias.r.baer@googlemail.com'
description = 'Useful tools for working with SymPy'
package_name = 'sympy_addons'
pypi_name = 'sympy-addons'
year = '2022'
url = 'https://github.com/maroba/sympy-addons'


def get_version():
    with open(os.path.join('sympy_addons', '__init__.py'), 'r') as f:
        lines = f.readlines()
        for line in lines:
            match = re.match(' *__version__ *= *\'([^\']+)\'', line)
            if match:
                return match.group(1)


version = get_version()

setup(
    name=pypi_name,
    author=author,
    author_email=email,
    url=url,
    version=version,
    packages=find_packages(),
    package_dir={package_name: package_name},
    include_package_data=True,
    license='MIT',
    description=description,
    long_description=open('README.md').read() if exists('README.md') else '',
    long_description_content_type="text/markdown",
    install_requires=['sympy', 'networkx'],
    test_requires=['pytest'],
    python_requires=">=3.6",
    classifiers=['Operating System :: OS Independent',
                 'Programming Language :: Python :: 3',
                 ],
    platforms=['ALL'],
)
