#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2017--, QIIME 2 development team.
#
# Distributed under the terms of the Lesser GPL 3.0 licence.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import find_packages, setup

setup(
    name='q2-coordinates',
    version='2018.11',
    license='BSD-3-Clause',
    packages=find_packages(),
    install_requires=['biom-format', 'pandas', 'scipy', 'cartopy', 'numpy',
                      'geopy', 'pysal-2.0rc2'],
    author="Nicholas Bokulich",
    author_email="nbokulich@gmail.com",
    description=("Methods for geographic mapping of qiime2 artifact data or"
                 "metadata."),
    url="https://github.com/nbokulich/q2-coordinates",
    entry_points={
        'qiime2.plugins':
        ['q2-coordinates=q2_coordinates.plugin_setup:plugin']
    },
    package_data={
        'q2_coordinates': ['assets/index.html', 'citations.bib'],
        'q2_coordinates.tests': ['data/*'],
    },
    zip_safe=False,
)
