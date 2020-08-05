import pandas as pd
import pandas.testing as pdt
import skbio
import q2_coordinates.qtrees as qtrees
from io import StringIO
import unittest


class BasicTest(unittest.TestCase):

    def setUp(self):
        test_dict = {'test_id_sw1': [-180.0, -90.0],
                     'test_id_nw1': [-180, 90],
                     'test_id_ne1': [180, 90],
                     'test_id_se1': [180, -90],
                     'test_id_sw2': [-91.0, -44.0],
                     'test_id_nw2': [-91, 44],
                     'test_id_ne2': [91, 44],
                     'test_id_se2': [91, -44]}
        self.test_df = pd.DataFrame.from_dict(
            test_dict,
            orient='index',
            columns=['longitude', 'latitude'])
        self.index = 'SampleID'
        self.test_df.index.name = self.index

        moved_dict = {'test_id_sw1': [0.0, 0.0],
                      'test_id_nw1': [0, 180],
                      'test_id_ne1': [360, 180],
                      'test_id_se1': [360, 0],
                      'test_id_sw2': [89.0, 46.0],
                      'test_id_nw2': [89, 134],
                      'test_id_ne2': [271, 134],
                      'test_id_se2': [271, 46]}
        self.moved_df = pd.DataFrame.from_dict(
            moved_dict,
            orient='index',
            columns=['longitude', 'latitude'])
        self.moved_df.index.name = self.index

        # create answer dataframe
        correct_dic = {'test_id_sw1': ['2', '3.3', '3', '3.3'],
                       'test_id_nw1': ['2', '1.1.', '1', '1.1'],
                       'test_id_ne1': ['2', '2.2.', '2', '2.2'],
                       'test_id_se1': ['2', '4.4.', '4', '4.4'],
                       'test_id_sw2': ['2', '3.1.', '3', '3.1'],
                       'test_id_nw2': ['2', '1.3.', '1', '1.3'],
                       'test_id_ne2': ['2', '2.4.', '2', '2.4'],
                       'test_id_se2': ['2', '4.2.', '4', '4.2']}

        # set the correct dataframe
        self.correct_dataframe = pd.DataFrame.from_dict(
            correct_dic,
            orient='index',
            columns=['depth', 'lineage',
                     'split-depth-1', 'split-depth-2'])
        self.correct_dataframe.index.name = self.index

        # set the correct tree
        self.correct_tree = skbio.TreeNode.read(
            StringIO(
                "((('test_id_sw1')'3.3', ('test_id_sw2')'3.1')'3.',"
                "(('test_id_nw1')'1.1.', ('test_id_nw2')'1.3.')'1.',"
                "(('test_id_se1')'4.4.', ('test_id_se2')'4.2.')'4.',"
                "(('test_id_ne1')'2.2.', ('test_id_ne2')'2.4.')'2.')root;"))

    # clean dataframe tests
    def test_clean_df(self):
        unclean_dic = {'test_id_sw': [-180, -90],
                       'test_id_nw': [-180, 90],
                       'test_id_ne': [180, 90],
                       'test_id_se': [180, -90],
                       'test_id_np': ["Not provided", "Not provided"],
                       'test_id_na': ["", ""]}

        to_clean_dataframe = pd.DataFrame.from_dict(
            unclean_dic,
            orient='index',
            columns=['longitude', 'latitude'])
        to_clean_dataframe.index.name = self.index

        correct_cleaned_points = {'test_id_sw': [0, 0],
                                  'test_id_nw': [0, 180],
                                  'test_id_ne': [360, 180],
                                  'test_id_se': [360, 0]}

        correct_cleaned_df = pd.DataFrame.from_dict(
            correct_cleaned_points,
            orient='index',
            columns=['longitude', 'latitude'])
        correct_cleaned_df.index.name = self.index
        correct_cleaned_df['latitude'] = correct_cleaned_df['latitude'].astype(float) # noqa
        correct_cleaned_df['longitude'] = correct_cleaned_df['longitude'].astype(float) # noqa

        cleaned = qtrees.clean(
             to_clean_dataframe, y_coord='latitude',
             x_coord='longitude', index='SampleID')

        pdt.assert_frame_equal(cleaned, correct_cleaned_df)

        lat_long_str_pts = [['test_id_np', "Not provided", "Not provided"],
                            ['test_id_na', "", ""]]
        str_only_df = pd.DataFrame(
            lat_long_str_pts,
            columns=['SampleID', 'longitude', 'latitude'])
        str_only_df = str_only_df.set_index(self.index)

        with self.assertRaises(ValueError):
            str_cleaned = qtrees.clean(str_only_df, 'latitude',
                                       'longitude', 'SampleID')

    def test_zero(self):
        pdt.assert_frame_equal(self.moved_df,
                               qtrees.clean(
                                   self.test_df, y_coord='latitude',
                                   x_coord='longitude', index='SampleID'))

        move_left_dict = {"test_1": {45.0, 45.0},
                          "test_2": {90, 90},
                          "test_3": {75, 90}}
        move_left_df = pd.DataFrame.from_dict(
            move_left_dict,
            orient='index',
            columns=['longitude', 'latitude'])
        move_left_df.index.name = self.index

        zero_left_dict = {"test_1": {0.0, 0.0},
                          "test_2": {45, 45},
                          "test_3": {30, 45}}
        zero_left_df = pd.DataFrame.from_dict(
            zero_left_dict,
            orient='index',
            columns=['longitude', 'latitude'])
        zero_left_df.index.name = self.index

        pdt.assert_frame_equal(move_left_df, zero_left_df)

    def test_get_results_outer(self):
        threshold = 2
        self.clean = qtrees.clean(self.test_df, y_coord='latitude',
                                  x_coord='longitude', index='SampleID')
        test_tree, test_samples = qtrees.get_results(self.moved_df,
                                                     threshold,
                                                     index='SampleID')
        pdt.assert_frame_equal(test_samples, self.correct_dataframe)
        self.assertEqual(test_tree.compare_subsets(self.correct_tree), 0.0)
        self.assertEqual(test_tree.compare_rfd(self.correct_tree), 0.0)

    def test_threshold(self):
        threshold = 1
        with self.assertRaises(ValueError):
            tree_1, samples_1 = qtrees.get_results(self.test_df, 
                                                   threshold, 
                                                   index='SampleID')
 
        threshold = 5
        correct_depth_pt = [['test_id_sw1', 1, '3.', 3],
                            ['test_id_nw1', 1, '1.', 1],
                            ['test_id_ne1', 1, '2.', 2],
                            ['test_id_se1', 1, '4.', 4],
                            ['test_id_sw2', 1, '3.', 3],
                            ['test_id_nw2', 1, '1.', 1],
                            ['test_id_ne2', 1, '2.', 2],
                            ['test_id_se2', 1, '4.', 4]]

        #Set the correct dataframe
        correct_depth_df = pd.DataFrame(
            correct_depth_pt,
            columns=['SampleID', 'depth', 'lineage', 'split-depth-1'])
        correct_depth_df = correct_depth_df.set_index('SampleID')
 
        tree_, samples_4 = qtrees.get_results(self.moved_df, threshold=5, index='SampleID')
        pdt.assert_frame_equal(samples_4, correct_depth_df)
        
        threshold = 8
        tree_8, samples_8 = qtrees.get_results(self.moved_df, threshold, index='SampleID')
        pdt.assert_frame_equal(samples_8, correct_depth1_df)


    # test the same dataframe to confirm consistant "mapping" 
    # to the same quadrants for boundary points
    def test_boundaries(self):
        boundary_points = [['test_1', 180, 90],
            ['test_2', 90, 90],
            ['test_3', 180, 45],
            ['test_4', 180, 135],
            ['test_5', 360.0, 90.0]]

        boundary_df =pd.DataFrame(
            boundary_points,
            columns = ['SampleID', 'longitude', 'latitude'])
        boundary_df = boundary_df.set_index('SampleID')
        

        boundary_points_2 = [['test_1', 180, 90],
            ['test_2', 90, 90],
            ['test_3', 180, 45],
            ['test_4', 180, 135],
            ['test_5', 360.0, 90.0]]

        boundary_df_2 =pd.DataFrame(
            boundary_points_2,
            columns = ['SampleID', 'longitude', 'latitude'])
        boundary_df_2 = boundary_df_2.set_index('SampleID')
        tree, samples = qtrees.get_results(boundary_df, 4, index='SampleID')
        tree_2, samples_2 = qtrees.get_results(boundary_df_2, 4, index='SampleID')
        pdt.assert_frame_equal(samples_2, samples)
 
if __name__ == '__main__':
    unittest.main()                
