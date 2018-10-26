# ----------------------------------------------------------------------------
# Copyright (c) 2017--, QIIME 2 development team.
#
# Distributed under the terms of the Lesser GPL 3.0 licence.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from .test_coordinates import CoordinatesTestPluginBase
from qiime2.plugins import coordinates
import qiime2
import pandas as pd
import numpy as np
from skbio import DistanceMatrix


# these tests make sure the actions run and accept appropriate inputs
class TestMapper(CoordinatesTestPluginBase):

    def setUp(self):
        super().setUp()

        alpha_fp = self.get_data_path('alpha_diversity.qza')
        self.alpha = qiime2.Artifact.load(alpha_fp)
        sample_md_fp = self.get_data_path('chardonnay.map.txt')
        sample_md = pd.read_csv(sample_md_fp, sep='\t', header=0, index_col=0)
        self.sample_md = qiime2.Metadata(sample_md)

    def test_draw_map_from_alpha_diversity_vector(self):
        coordinates.actions.draw_map(
            metadata=self.sample_md.merge(self.alpha.view(qiime2.Metadata)),
            latitude='latitude', longitude='longitude', column='observed_otus')

    def test_draw_map_from_sample_metadata(self):
        coordinates.actions.draw_map(
            metadata=self.sample_md, latitude='latitude',
            longitude='longitude', column='vineyard', discrete=True)

    def test_distance_matrix_geodesic(self):
        dm, = coordinates.actions.distance_matrix(
            metadata=self.sample_md, latitude='latitude',
            longitude='longitude')
        exp = qiime2.Artifact.load(self.get_data_path('dm.qza'))
        self.assertTrue(dm.view(DistanceMatrix) == exp.view(DistanceMatrix))
