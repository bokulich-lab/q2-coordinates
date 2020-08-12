from q2_coordinates.plugin_setup import (
    QuadTree, QuadTreeFormat, QuadTreeDirectoryFormat)
from q2_types.sample_data import SampleData
import tempfile
import shutil
import pkg_resources
from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin import ValidationError
import pandas as pd
import pandas.testing as pdt
import qiime2


class QuadTreeTestPluginBase(TestPluginBase):
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


class TestSemanticTypeQuad(QuadTreeTestPluginBase):
    def test_quadtree_format_validate_positive(self):
        filepath = self.get_data_path('quadtree.tsv')
        format = QuadTreeFormat(filepath, mode='r')
        format.validate()

    def test_quadtree_format_validate_negative(self):
        filepath = self.get_data_path('bad_quadtrees.tsv')
        format = QuadTreeFormat(filepath, mode='r')
        with self.assertRaisesRegex(ValidationError, 'QuadTreeFormat'):
            format.validate()

    def test_quadtree_dir_fmt_validate_positive(self):
        filepath = self.get_data_path('quadtree.tsv')
        shutil.copy(filepath, self.temp_dir.name)
        format = QuadTreeDirectoryFormat(self.temp_dir.name, mode='r')
        format.validate()

    def test_quadtree_semantic_type_registration(self):
        self.assertRegisteredSemanticType(QuadTree)

    def test_sample_data_quadtree_to_quadtree_dir_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            SampleData[QuadTree], QuadTreeDirectoryFormat)

    def test_pd_dataframe_to_quadtree_format(self):
        transformer = self.get_transformer(pd.DataFrame, QuadTreeFormat)
        exp = pd.DataFrame(
            {'#SampleID': ('test_1', 'test_2', 'test_3', 'test_4'),
             'depth': ('2', '2', '2', '2'),
             'lineage': ('1.2.', '1.3.', '1.2.', '1.3.'),
             'split_depth_1': ('1', '1', '1', '1'),
             'split_depth_2': ('1.2', '1.3', '1.2', '1.3')}, dtype=object)
        exp = exp.set_index('#SampleID')
        obs = transformer(exp)
        obs = pd.read_csv(str(obs), sep='\t', index_col=0, dtype=object)
        pdt.assert_frame_equal(exp, obs)

    def test_quadtree_format_to_pd_dataframe(self):
        _, obs = self.transform_format(
            QuadTreeFormat, pd.DataFrame, 'quadtree.tsv')
        exp = pd.DataFrame(
            {'#SampleID': ('test_1', 'test_2', 'test_3', 'test_4'),
             'depth': ('2', '2', '2', '2'),
             'lineage': ('1.2.', '1.3.', '1.2.', '1.3.'),
             'split_depth_1': ('1', '1', '1', '1'),
             'split_depth_2': ('1.2', '1.3', '1.2', '1.3')}, dtype=object)
        exp = exp.set_index('#SampleID')
        pdt.assert_frame_equal(exp, obs)

    def test_quadtree_format_to_metadata(self):
        _, obs = self.transform_format(
            QuadTreeFormat, qiime2.Metadata, 'quadtree.tsv')
        obs_category = obs.get_column('split_depth_1')
        exp_index = pd.Index(['test_1', 'test_2', 'test_3', 'test_4'],
                             name='#SampleID', dtype=object)
        exp = pd.Series(['1', '1', '1', '1'],
                        name='split_depth_1', index=exp_index)
        pdt.assert_series_equal(exp, obs_category.to_series())
