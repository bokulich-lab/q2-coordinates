# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from q2_coordinates.plugin_setup import (
    CoordinatesFormat, CoordinatesDirectoryFormat, Coordinates)
from q2_types.sample_data import SampleData
import tempfile
import shutil
import pkg_resources
from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin import ValidationError
import pandas as pd
import qiime2


class CoordinatesTestPluginBase(TestPluginBase):
    package = 'q2_coordinates.tests'

    def setUp(self):
        super().setUp()
        self.temp_dir = tempfile.TemporaryDirectory(
            prefix='q2-coordinates-test-temp-')

    def tearDown(self):
        self.temp_dir.cleanup()

    def get_data_path(self, filename):
        return pkg_resources.resource_filename(self.package,
                                               'data/%s' % filename)

    def load_md(self, md_fn):
        md_fp = self.get_data_path(md_fn)
        sample_md = pd.read_csv(md_fp, sep='\t', header=0, index_col=0)
        return qiime2.Metadata(sample_md)


class TestSemanticTypes(CoordinatesTestPluginBase):

    def test_coordinates_format_validate_positive(self):
        filepath = self.get_data_path('coordinates.tsv')
        format = CoordinatesFormat(filepath, mode='r')
        format.validate()

    def test_coordinates_format_validate_negative(self):
        filepath = self.get_data_path('false-coordinates.tsv')
        format = CoordinatesFormat(filepath, mode='r')
        with self.assertRaisesRegex(ValidationError, 'CoordinatesFormat'):
            format.validate()

    def test_coordinates_dir_fmt_validate_positive(self):
        filepath = self.get_data_path('coordinates.tsv')
        shutil.copy(filepath, self.temp_dir.name)
        format = CoordinatesDirectoryFormat(self.temp_dir.name, mode='r')
        format.validate()

    def test_coordinates_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Coordinates)

    def test_sample_data_coordinates_to_coordinates_dir_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[Coordinates], CoordinatesDirectoryFormat)

    def test_pd_dataframe_to_coordinates_format(self):
        transformer = self.get_transformer(pd.DataFrame, CoordinatesFormat)
        exp = pd.DataFrame(
            {'Latitude': (38.306, 38.306), 'Longitude': (-122.228, -122.228)})
        obs = transformer(exp)
        obs = pd.read_csv(str(obs), sep='\t', header=0, index_col=0)
        self.assertEqual(sorted(exp), sorted(obs))

    def test_coordinates_format_to_pd_dataframe(self):
        _, obs = self.transform_format(
            CoordinatesFormat, pd.DataFrame, 'coordinates.tsv')
        exp = pd.DataFrame(
            {'Latitude': (38.306, 38.306, 38.306, 38.306),
             'Longitude': (-122.228, -122.228, -122.228, -122.228)},
            index=['a', 'b', 'c', 'd'])
        self.assertEqual(sorted(exp), sorted(obs))

    def test_coordinates_format_to_metadata(self):
        _, obs = self.transform_format(
            CoordinatesFormat, qiime2.Metadata, 'coordinates.tsv')
        obs_category = obs.get_column('Latitude')
        exp_index = pd.Index(['a', 'b', 'c', 'd'], dtype=object)
        exp = pd.Series(['38.306', '38.306', '38.306', '38.306'],
                        name='Latitude', index=exp_index)
        self.assertEqual(sorted(exp), sorted(obs_category.to_series()))
