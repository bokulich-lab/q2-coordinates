# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import find_packages, setup

setup(
    name='q2-coordinates',
    version='2020.8.1.dev',
    license='BSD-3-Clause',
    packages=find_packages(),
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
        'q2_coordinates': ['assets/index.html', 'assets/animated_map/*',
                           'assets/animated_map/*/*/*',
                           'citations.bib'],
        'q2_coordinates.tests': ['data/*'],
    },
    zip_safe=False,
)
