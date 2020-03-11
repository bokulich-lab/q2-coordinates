import pandas as pd
import pandas.testing as pdt
import numpy as np
import skbio
import unittest
import qtrees as qtrees
from io import StringIO
import numpy.testing as npt
#test every path through code including exception raising for comprehension

class BasicTest(unittest.TestCase):
        def setUp(self):
            #setup function for data creation

            #set the starting input
            test_points = [['test_id_sw1', -180.0, -90.0],
                ['test_id_nw1', -180, 90],
                ['test_id_ne1', 180, 90],
                ['test_id_se1', 180, -90],
                ['test_id_sw2', -91.0, -44.0],
                ['test_id_nw2', -91, 44],
                ['test_id_ne2', 91, 44], 
                ['test_id_se2', 91, -44]]
            test_df =pd.DataFrame(test_points,
                columns = ['index', 'longitude', 'latitude'])
            
            test_df['latitude'] = test_df['latitude'] + 90

            test_df['longitude'] = test_df['longitude'] + 180

            self.test_df = test_df.set_index("index")
            
            #create answer dataframe
            correct_point = [['test_id_sw1', '3.', '3.3.'], 
                ['test_id_nw1', '1.', '1.1.'],
                ['test_id_ne1', '2.', '2.2.'],
                ['test_id_se1', '4.', '4.4.'],
                ['test_id_sw2', '3.', '3.1.'],
                ['test_id_nw2', '1.', '1.3.'],
                ['test_id_ne2', '2.', '2.4.'],
                ['test_id_se2', '4.', '4.2.']]
            
            #Set the correct dataframe
            correct_dataframe = pd.DataFrame(correct_point, 
                columns=['index', 'H1', 'H2'])
            self.correct_dataframe = correct_dataframe.set_index('index')
            
            #set the correct tree
            #this needs to be fixed
            self.correct_tree = skbio.TreeNode.read(StringIO(
                "((('test_id_sw1')'3.3',('test_id_sw2')'3.1')'3.', (('test_id_nw1')'1.1.',('test_id_nw2')'1.3.')'1.', (('test_id_se1')'4.4.', ('test_id_se2')'4.2.')'4.', (('test_id_ne1')'2.2.',('test_id_ne2')'2.4.')'2.')root;"))

        #clean dataframe tests
        def test_clean_df(self):
            incorrect_points = [['test_id_sw', -180, -90],
                ['test_id_nw', -180, 90],['test_id_ne', 180, 90], 
                ['test_id_se', 180, -90],
                ['test_id_np', "Not provided", "Not provided"],
                ['test_id_na', "", ""]]
            to_clean_dataframe = pd.DataFrame(incorrect_points, 
                columns=['index', 'longitude', 'latitude'])
            to_clean_dataframe = to_clean_dataframe.set_index('index')

            
            correct_cleaned_points = [['test_id_sw', 0, 0],
                ['test_id_nw', 0, 180],['test_id_ne', 360, 180], 
                ['test_id_se', 360, 0]]
            
            correct_cleaned_df =pd.DataFrame(correct_cleaned_points, 
                columns = ['index', 'longitude', 'latitude'])

            correct_cleaned_df = correct_cleaned_df.set_index("index")
            

            correct_cleaned_df['latitude'] = correct_cleaned_df['latitude'].astype(float)
            correct_cleaned_df['longitude'] = correct_cleaned_df['longitude'].astype(float)

            
            cleaned =qtrees.clean(to_clean_dataframe)
            pdt.assert_frame_equal(cleaned, correct_cleaned_df)
            

            lat_long_str_pts = [['test_id_np', "Not provided", "Not provided"],
                ['test_id_na', "", ""]]
            str_only_df = pd.DataFrame(lat_long_str_pts,
                columns=['index', 'longitude', 'latitude'])
            str_only_df = str_only_df.set_index('index')


            with self.assertRaises(ValueError): 
                str_cleaned = qtrees.clean(str_only_df)
            
        def test_get_results_outer(self):
            threshold = 2
            test_tree, test_samples = qtrees.get_results(self.test_df, threshold)
            pdt.assert_frame_equal(test_samples, self.correct_dataframe) 
            self.assertEqual(test_tree.compare_subsets(self.correct_tree), 0.0)
            self.assertEqual(test_tree.compare_rfd(self.correct_tree), 0.0)

        def test_threshold(self):
            threshold = 1
            with self.assertRaises(ValueError):
                tree_1, samples_1 = qtrees.get_results(self.test_df, threshold)
            
            
            threshold = 5
            correct_depth1_pt = [['test_id_sw1', '3.'],
                ['test_id_nw1', '1.'],
                ['test_id_ne1', '2.'],
                ['test_id_se1', '4.'],
                ['test_id_sw2', '3.'],
                ['test_id_nw2', '1.'],
                ['test_id_ne2', '2.'],
                ['test_id_se2', '4.']]

            #Set the correct dataframe
            correct_depth1_df = pd.DataFrame(correct_depth1_pt,
                columns=['index', 'H1'])
            correct_depth1_df = correct_depth1_df.set_index('index')


            tree_4, samples_4 = qtrees.get_results(self.test_df, threshold)
            pdt.assert_frame_equal(samples_4, correct_depth1_df)
            
            #what to do when threshold is higher than number of samples?
            threshold = 8
            tree_8, samples_8 = qtrees.get_results(self.test_df, threshold)
            pdt.assert_frame_equal(samples_8, correct_depth1_df)
        
        #def test_build_samples(self):
                

        #def test_build_tree(self):
            
        
        #test the same dataframe to confirm consistant "mapping" to the same quadrants for
        #boundary points
        def test_boundaries(self):
            boundary_points = [['test_1', 180, 90],
                ['test_2', 90, 90],
                ['test_3', 180, 45],
                ['test_4', 180, 135],
                ['test_5', 360.0, 90.0]]

            boundary_df =pd.DataFrame(boundary_points,
                columns = ['index', 'longitude', 'latitude'])
            boundary_df = boundary_df.set_index('index')
            

            boundary_points_2 = [['test_1', 180, 90],
                ['test_2', 90, 90],
                ['test_3', 180, 45],
                ['test_4', 180, 135],
                ['test_5', 360.0, 90.0]]

            boundary_df_2 =pd.DataFrame(boundary_points_2,
                columns = ['index', 'longitude', 'latitude'])
            boundary_df_2 = boundary_df_2.set_index('index')
            tree, samples = qtrees.get_results(boundary_df, 4)
            tree_2, samples_2 = qtrees.get_results(boundary_df_2, 4)
            pdt.assert_frame_equal(samples_2, samples)
            
if __name__ == '__main__':
    unittest.main()                
