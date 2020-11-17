# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.img_tiles import StamenTerrain, OSM, GoogleTiles
import math
from os.path import join
import pkg_resources
import q2templates


TEMPLATES = pkg_resources.resource_filename('q2_coordinates', 'assets')


def _load_and_validate(metadata, columns, names, missing_data):
    # load and drop empty data
    metadata = metadata.to_dataframe()
    metadata = metadata[columns]
    if missing_data == 'error' and metadata.isnull().values.any():
        raise ValueError(
            'One or more samples are missing metadata. Check inputs or use '
            'missing_data=True to drop these samples and ignore this error.')
    metadata = metadata.dropna()

    # validate inputs
    _validate_columns(metadata, columns, names)

    return metadata


def _validate_columns(metadata, columns, names):
    for c, name in zip(columns, names):
        if c in metadata:
            pass
        else:
            raise ValueError(
                'Must define a valid "{0}" column to use for sample mapping. '
                '"{1}" is not a valid column name in your sample metadata '
                'file.'.format(name, c))


def get_map_params(image='StamenTerrain', color_palette=None):
    # set color palette
    if color_palette:
        cmap = plt.get_cmap(color_palette)
    else:
        cmap = None

    # set background image
    if image == 'StamenTerrain':
        tiler = StamenTerrain()
    elif image == 'GoogleTiles':
        tiler = GoogleTiles()
    elif image == 'OSM':
        tiler = OSM()

    return cmap, tiler


def get_max_extent(latitude, longitude):
    lat_0 = latitude.min() - latitude.std()
    lat_1 = latitude.max() + latitude.std()
    lon_0 = longitude.min() - longitude.std()
    lon_1 = longitude.max() + longitude.std()
    return lat_0, lat_1, lon_0, lon_1


def plot_basemap(latitude, longitude, image, color_palette=None):
    # define basemap, color palette
    cmap, tiler = get_map_params(image, color_palette)

    # Find min/max coordinates to set extent
    lat_0, lat_1, lon_0, lon_1 = get_max_extent(latitude, longitude)

    # Automatically focus resolution
    max_span = max((abs(lat_1) - abs(lat_0)), (abs(lon_1) - abs(lon_0)))
    res = int(-1.4 * math.log1p(max_span) + 13)

    # initiate tiler projection
    ax = plt.axes(projection=tiler.crs)
    # Define extents of any plotted data
    ax.set_extent((lon_0, lon_1, lat_0, lat_1), ccrs.Geodetic())
    # add terrain background
    ax.add_image(tiler, res)

    return ax, cmap


def save_map(ax, output_dir):
    ax.get_figure().savefig(
        join(output_dir, 'plot.png'), bbox_inches='tight')
    ax.get_figure().savefig(
        join(output_dir, 'plot.pdf'), bbox_inches='tight')
    plt.close('all')


def mapviz(output_dir, results=None, title='Coordinates'):
    if results is not None:
        results.to_csv(join(
            output_dir, 'results.tsv'), sep='\t', index=True)
        results = q2templates.df_to_html(results)
    else:
        results = False

    index = join(TEMPLATES, 'index.html')
    q2templates.render(index, output_dir, context={
        'results': results,
        'title': title})
