#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2017--, q2-coordinates development team.
#
# Distributed under the terms of the Lesser GPL 3.0 licence.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


from qiime2.plugin import Str, Plugin, Metadata, Choices, Bool
from .mapper import map_metadata_coordinates, map_predicted_coordinates
import q2_coordinates
import importlib
from q2_types.sample_data import AlphaDiversity, SampleData
from q2_types.sample_data import SampleData
from q2_sample_classifier.plugin_setup import Coordinates


plugin = Plugin(
    name='coordinates',
    version=q2_coordinates.__version__,
    website="https://github.com/nbokulich/q2-coordinates",
    package='q2_coordinates'
)


base_parameters={
    'metadata': Metadata,
    'latitude': Str,
    'longitude': Str,
    'image': Str % Choices(['StamenTerrain', 'OSM', 'GoogleTiles']),
}

base_parameter_descriptions={
    'metadata': 'The sample metadata containing latitude and longitude data.',
    'latitude': 'Metadata category containing latitude in decimal degrees.',
    'longitude': 'Metadata category containing longitude in decimal degrees.',
    'image': 'Base map image to use for coordinate projection.',
}


plugin.visualizers.register_function(
    function=map_metadata_coordinates,
    inputs={'alpha_diversity': SampleData[AlphaDiversity],
    },
    parameters={**base_parameters,
                'category': Str,
                'color_palette': Str,
                'discrete': Bool,
                },
    input_descriptions={
        'alpha_diversity': 'Vector of alpha diversity values by sample.',
    },
    parameter_descriptions={
        **base_parameter_descriptions,
        'category': ('Metadata category to use for coloring sample points. If '
                     'none is supplied, will use alpha_diversity artifact for '
                     'coloring.'),
        'color_palette': (
            'Color palette to use for coloring sample points on map.'),
        'discrete': 'Plot continuous category data as discrete values.'
    },
    name='Plot sampling site geocoordinates on a map.',
    description=(
        'Plots sample geocoordinates onto a map image. The input metadata'
        'map should contain the categories "category", "latitude", and '
        '"longitude" for each sample. Sample points are colored by the '
        'column name "category", which may be categorical or continuous, and '
        'may be located in the sample metadata or in the AlphaDiversity '
        'artifact (until optional artifact inputs are supported, the latter '
        'is a required input whether or not you wish to categorize by alpha '
        'diversity). For a list of available color palettes, see '
        'https://matplotlib.org/examples/color/colormaps_reference.html. '
        'Use qualitative colormaps with maximal contrast against map '
        'background, such as "Set1", "Accent", "Paired", "Dark2", or "tab10".')
)


plugin.visualizers.register_function(
    function=map_predicted_coordinates,
    inputs={'predictions': SampleData[Coordinates],
            'prediction_regression': SampleData[Coordinates],
    },
    parameters={**base_parameters,
                'pred_lat': Str,
                'pred_long': Str,
                },
    input_descriptions={
        'predictions': 'Predicted geospatial coordinates for each sample.',
        'prediction_regression': (
            'Prediction regression results for each coordinate.'),
    },
    parameter_descriptions={
        **base_parameter_descriptions,
        'pred_lat': ('Name of category in predictions input containing '
                     'predicted latitude in decimal degrees.'),
        'pred_long': ('Name of category in predictions input containing '
                     'predicted longitude in decimal degrees.'),
    },
    name='Plot predicted and actual geocoordinates on a map.',
    description=(
        'Plots predicted and actual sample geocoordinates onto a map image, '
        'e.g., the output of q2-sample-classifier visualizer '
        'predict_coordinates. The input metadata map must contain the '
        'categories "latitude", and "longitude" for each sample. The input '
        '"predictions" artifact must contain the categories "pred_lat", and '
        '"pred_long" for each sample. Sample points are colored by expected '
        'vs. predicted values.')
)
