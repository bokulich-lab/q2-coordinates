# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


from qiime2.plugin import (Str, Plugin, Metadata, Choices, Bool, Citations,
                           Int, MetadataColumn, Numeric, Range)
from .mapper import (draw_map, geodesic_distance, euclidean_distance,
                     draw_interactive_map)
import q2_coordinates
import importlib
from q2_types.sample_data import SampleData
from q2_types.distance_matrix import DistanceMatrix
from ._format import (CoordinatesFormat, CoordinatesDirectoryFormat)
from ._type import (Coordinates)
from .stats import autocorr


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
    'missing_data': Str
}

base_parameter_descriptions = {
    'metadata': 'The sample metadata containing coordinate data.',
    'latitude': 'Metadata column containing latitude in decimal degrees.',
    'longitude': 'Metadata column containing longitude in decimal degrees.',
    'missing_data': 'If "error" (default), will raise an error if any '
                    'metadata columns are missing data. Set to "ignore" to '
                    'silently drop rows (samples) that are missing data.'
}


plugin.visualizers.register_function(
    function=draw_map,
    inputs={},
    parameters={**base_parameters,
                'column': Str,
                'color_palette': Str % Choices([
                    'Set1', 'Set2', 'Set3', 'Pastel1', 'Pastel2', 'Paired',
                    'Accent', 'Dark2', 'tab10', 'tab20', 'tab20b', 'tab20c',
                    'viridis', 'plasma', 'inferno', 'magma', 'terrain',
                    'rainbow']),
                'discrete': Bool,
                'image': Str % Choices(
                    ['StamenTerrain', 'OSM', 'GoogleTiles']),
                },
    input_descriptions={},
    parameter_descriptions={
        **base_parameter_descriptions,
        'column': ('Metadata column to use for coloring sample points. If '
                   'none is supplied, will use alpha_diversity artifact for '
                   'coloring.'),
        'color_palette': (
            'Color palette to use for coloring sample points on map.'),
        'discrete': 'Plot continuous column data as discrete values.',
        'image': 'Base map image to use for coordinate projection.'},
    name='Plot sampling site geocoordinates on a map.',
    description=('Plots sample data onto a map using sample geocoordinates. '
                 'Sample points are colored by the column name "column", '
                 'which may be categorical or numeric. Note that samples with '
                 'missing values are silently dropped.'),
    citations=[citations['Cartopy']]
)

plugin.visualizers.register_function(
    function=draw_interactive_map,
    inputs={},
    parameters={**base_parameters,
                'column': Str,
                'color_palette': Str % Choices([
                    'Set1', 'Set2', 'Set3', 'Pastel1', 'Pastel2', 'Paired',
                    'Accent', 'Dark2', 'tab10', 'tab20', 'tab20b', 'tab20c',
                    'viridis', 'plasma', 'inferno', 'magma', 'terrain',
                    'rainbow']),
                'discrete': Bool,
                'image': Str % Choices(
                    ['StamenTerrain', 'OSM', 'GoogleTiles']),
                },
    input_descriptions={},
    parameter_descriptions={
        **base_parameter_descriptions,
        'column': ('Metadata column to use for coloring sample points. If '
                   'none is supplied, will use alpha_diversity artifact for '
                   'coloring.'),
        'color_palette': (
            'Color palette to use for coloring sample points on map.'),
        'discrete': 'Plot continuous column data as discrete values.'},
    name='Plot sampling site geocoordinates on a map.',
    description=('Plots sample data onto an interactive OpenLayers map using '
                 'sample geocoordinates. Sample points are colored by the '
                 'column name "column", which may be categorical or numeric. '
                 'Note that samples with missing values are silently '
                 'dropped.'),
    citations=[citations['Cartopy']]
)

plugin.methods.register_function(
    function=geodesic_distance,
    inputs={},
    parameters=base_parameters,
    outputs=[('distance_matrix', DistanceMatrix)],
    input_descriptions={},
    parameter_descriptions=base_parameter_descriptions,
    name='Create a distance matrix from sample geocoordinates.',
    description='Measure pairwise geodesic distances between coordinates. '
                'Output distances are reported in meters. '
                'Note that samples with missing values are silently dropped.',
    citations=[citations['Karney2013']]
)

coords_description = ('Name of metadata column containing {0}-axis coordinate '
                      'in cartesian space.')

plugin.methods.register_function(
    function=euclidean_distance,
    inputs={},
    parameters={'metadata': Metadata,
                'x': Str,
                'y': Str,
                'z': Str,
                'missing_data': Str},
    outputs=[('distance_matrix', DistanceMatrix)],
    input_descriptions={},
    parameter_descriptions={
        'metadata': base_parameter_descriptions['metadata'],
        'x': coords_description.format('x'),
        'y': coords_description.format('y'),
        'z': coords_description.format('z'),
        'missing_data': base_parameter_descriptions['missing_data']},
    name='Create a distance matrix from 2D or 3D cartesian coordinates.',
    description='Measure pairwise euclidean distances between cartesian '
                'coordinates. '
                'Note that samples with missing values are silently dropped.',
)

plugin.visualizers.register_function(
    function=autocorr,
    inputs={'distance_matrix': DistanceMatrix},
    parameters={'metadata': MetadataColumn[Numeric],
                'permutations': Int % Range(0, None),
                'two_tailed': Bool,
                'transformation': Str % Choices(['R', 'B', 'D', 'V']),
                'intersect_ids': Bool},
    input_descriptions={'distance_matrix': 'Spatial distance matrix'},
    parameter_descriptions={
        'metadata': 'Variable to test for spatial autocorrelation.',
        'permutations': 'Number of random permutations for calculation of '
                        'pseudo p-values.',
        'two_tailed': 'If True (default) analytical p-values for Moran are '
                      'two tailed, otherwise if False, they are one-tailed. '
                      'This does not apply to Geary\'s C.',
        'transformation': 'Weights transformation, default is "R" '
                          '(row-standardized). Other options include "B": '
                          'binary, "D": doubly-standardized, "V": '
                          'variance-stabilizing.',
        'intersect_ids': 'If supplied, IDs that are not found in both the '
                         'distance matrix and metadata will be discarded '
                         'before testing. Default behavior is to error on any '
                         'mismatched IDs.'},
    name='Compute Moran\'s I and Geary\'s C autocorrelation statistics.',
    description='Compute Moran\'s I and Geary\'s C autocorrelation statistics '
                'on a (geo)spatial distance matrix and an independent '
                'variable.',
    citations=[citations['Moran'], citations['Geary']]
)


# Registrations
plugin.register_formats(CoordinatesFormat, CoordinatesDirectoryFormat)

plugin.register_semantic_types(Coordinates)

plugin.register_semantic_type_to_format(
    SampleData[Coordinates],
    artifact_format=CoordinatesDirectoryFormat)

importlib.import_module('q2_coordinates._transformer')
