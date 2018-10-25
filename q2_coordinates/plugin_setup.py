#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2017--, QIIME 2 development team.
#
# Distributed under the terms of the Lesser GPL 3.0 licence.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


from qiime2.plugin import Str, Plugin, Metadata, Choices, Bool, Citations
from .mapper import draw_map
import q2_coordinates
import importlib
from q2_types.sample_data import SampleData
from ._format import (CoordinatesFormat, CoordinatesDirectoryFormat)
from ._type import (Coordinates)


citations = Citations.load('citations.bib', package='q2_coordinates')

plugin = Plugin(
    name='coordinates',
    version=q2_coordinates.__version__,
    website="https://github.com/nbokulich/q2-coordinates",
    package='q2_coordinates',
    description=(
        'This QIIME 2 plugin supports methods for geospatial analysis and map '
        'building.'),
    short_description=(
        'Plugin for geospatial analysis and cartography.'),
)


base_parameters = {
    'metadata': Metadata,
    'latitude': Str,
    'longitude': Str,
    'image': Str % Choices(['StamenTerrain', 'OSM', 'GoogleTiles']),
}

base_parameter_descriptions = {
    'metadata': 'The sample metadata containing latitude and longitude data.',
    'latitude': 'Metadata column containing latitude in decimal degrees.',
    'longitude': 'Metadata column containing longitude in decimal degrees.',
    'image': 'Base map image to use for coordinate projection.',
}


plugin.visualizers.register_function(
    function=draw_map,
    inputs={},
    parameters={**base_parameters,
                'column': Str,
                'color_palette': Str,
                'discrete': Bool,
                },
    input_descriptions={},
    parameter_descriptions={
        **base_parameter_descriptions,
        'column': ('Metadata column to use for coloring sample points. If '
                   'none is supplied, will use alpha_diversity artifact for '
                   'coloring.'),
        'color_palette': (
            'Color palette to use for coloring sample points on map.'),
        'discrete': 'Plot continuous column data as discrete values.'
    },
    name='Plot sampling site geocoordinates on a map.',
    description=(
        'Plots sample geocoordinates onto a map image. The input metadata'
        'map should contain the categories "column", "latitude", and '
        '"longitude" for each sample. Sample points are colored by the '
        'column name "column", which may be categorical or continuous, and '
        'may be located in the sample metadata or in the AlphaDiversity '
        'artifact (until optional artifact inputs are supported, the latter '
        'is a required input whether or not you wish to categorize by alpha '
        'diversity). For a list of available color palettes, see '
        'https://matplotlib.org/examples/color/colormaps_reference.html. '
        'Use qualitative colormaps with maximal contrast against map '
        'background, such as "Set1", "Accent", "Paired", "Dark2", or "tab10".')
)


# Registrations
plugin.register_formats(CoordinatesFormat, CoordinatesDirectoryFormat)

plugin.register_semantic_types(Coordinates)

plugin.register_semantic_type_to_format(
    SampleData[Coordinates],
    artifact_format=CoordinatesDirectoryFormat)

importlib.import_module('q2_coordinates._transformer')
