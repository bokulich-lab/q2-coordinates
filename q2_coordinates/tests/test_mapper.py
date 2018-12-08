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
import numpy as np
from skbio import DistanceMatrix


# these tests make sure the actions run and accept appropriate inputs
class TestMapper(CoordinatesTestPluginBase):

    def setUp(self):
        super().setUp()

        alpha_fp = self.get_data_path('alpha_diversity.qza')
        self.alpha = qiime2.Artifact.load(alpha_fp)
        self.sample_md = self.load_md('chardonnay_sample_metadata.txt')

    def test_draw_map_from_alpha_diversity_vector(self):
        coordinates.actions.draw_map(
            metadata=self.sample_md.merge(self.alpha.view(qiime2.Metadata)),
            latitude='latitude', longitude='longitude', column='observed_otus')

    def test_draw_map_from_sample_metadata(self):
        coordinates.actions.draw_map(
            metadata=self.sample_md, latitude='latitude',
            longitude='longitude', column='vineyard', discrete=True)

    def test_geodesic_distance(self):
        dm, = coordinates.actions.geodesic_distance(
            metadata=self.sample_md, latitude='latitude',
            longitude='longitude')
        exp = qiime2.Artifact.load(self.get_data_path(
            'geodesic_distance_matrix.qza')).view(DistanceMatrix)
        dm = dm.view(DistanceMatrix)
        error_msg = 'observed IDs: {0}\nexpected IDs: {1}'
        self.assertTrue(dm == exp, msg=error_msg.format(dm.ids, exp.ids))


class TestCoordMethods(CoordinatesTestPluginBase):

    def setUp(self):
        super().setUp()

        self.coord_md = self.load_md('xyz-coordinates.tsv')

    def test_euclidean_distance_3d(self):
        dm, = coordinates.actions.euclidean_distance(
            metadata=self.coord_md, x='x', y='y', z='z')
        dm = dm.view(DistanceMatrix).condensed_form()
        exp = np.array([1.30384048, 3.98998747, 4.26848919, 5.17010638,
                        5.62316637, 2.82488938, 3.02324329, 3.93319209,
                        4.37035468, 0.81240384, 2.16564078, 2.28473193,
                        1.37477271, 1.55563492, 0.57445626])
        np.testing.assert_allclose(dm, exp)

    def test_euclidean_distance_2d(self):
        dm, = coordinates.actions.euclidean_distance(
            metadata=self.coord_md, x='x', y='y')
        dm = dm.view(DistanceMatrix).condensed_form()
        exp = np.array([1.30384048, 3.98497177, 4.25793377, 5.0039984,
                        5.51452627, 2.81780056, 3.00832179, 3.71214224,
                        4.2296572,  0.64031242, 1.56204994, 1.87882942,
                        0.94339811, 1.33416641, 0.53851648])
        np.testing.assert_allclose(dm, exp)
