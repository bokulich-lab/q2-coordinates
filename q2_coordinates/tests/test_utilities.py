# ----------------------------------------------------------------------------
# Copyright (c) 2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import unittest

import pandas as pd
import qiime2

from q2_coordinates._utilities import get_max_extent


class TestUtils(unittest.TestCase):

    def test_get_max_extent_1(self):
        lat = pd.Series([-66.0, -64.0, -62.0])
        lon = pd.Series([26.0, 28.0, 30.0])

        obs = get_max_extent(lat, lon)
        exp = (-66.3, -61.7, 25.7, 30.3)
        self.assertTupleEqual(obs, exp)

    def test_get_max_extent_2(self):
        lat = pd.Series([66.0, 64.0, 62.0])
        lon = pd.Series([-26.0, -28.0, -30.0])

        obs = get_max_extent(lat, lon)
        exp = (61.7, 66.3, -30.3, -25.7)
        self.assertTupleEqual(obs, exp)

    def test_get_max_extent_3(self):
        lat = pd.Series([-88.0, 10.0, 82.0])
        lon = pd.Series([-175.0, 15.5, 168.4])

        obs = get_max_extent(lat, lon)
        exp = (-90, 90, -180, 180)
        self.assertTupleEqual(obs, exp)
