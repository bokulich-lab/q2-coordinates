#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2017--, q2-coordinates development team.
#
# Distributed under the terms of the Lesser GPL 3.0 licence.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


from qiime2.plugin import Str, Plugin, Metadata, Choices, Bool
from .mapper import map_metadata_coordinates
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


Coordinates = SemanticType('Coordinates', variant_of=SampleData.field['type'])


class CoordinatesFormat(model.TextFileFormat):
    def sniff(self):
        with self.open() as fh:
            for line, _ in zip(fh, range(10)):
                cells = line.split('\t')
                if len(cells) < 2:
                    return False
            return True


CoordinatesDirectoryFormat = model.SingleFileDirectoryFormat(
    'CoordinatesDirectoryFormat', 'coordinates.tsv',
    CoordinatesFormat)


def _read_dataframe(fh):
    # Using `dtype=object` and `set_index` to avoid type casting/inference
    # of any columns or the index.
    df = pd.read_csv(fh, sep='\t', header=0, dtype=object)
    df.set_index(df.columns[0], drop=True, append=False, inplace=True)
    df.index.name = None
    return df


@plugin.register_transformer
def _1(data: pd.DataFrame) -> (CoordinatesFormat):
    ff = CoordinatesFormat()
    with ff.open() as fh:
        data.to_csv(fh, sep='\t', header=True)
    return ff


@plugin.register_transformer
def _2(ff: CoordinatesFormat) -> (pd.DataFrame):
    with ff.open() as fh:
        df = _read_dataframe(fh)
        return df.apply(lambda x: pd.to_numeric(x, errors='ignore'))


@plugin.register_transformer
def _3(ff: CoordinatesFormat) -> (qiime2.Metadata):
    with ff.open() as fh:
        return qiime2.Metadata(_read_dataframe(fh))


plugin.register_formats(CoordinatesFormat, CoordinatesDirectoryFormat)

plugin.register_semantic_types(Coordinates, BooleanSeries)

plugin.register_semantic_type_to_format(
    SampleData[Coordinates],
    artifact_format=CoordinatesDirectoryFormat)

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
