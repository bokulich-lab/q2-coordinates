# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.cm as cm
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.patches as mpatch
import qiime2
import scipy

from skbio import DistanceMatrix
from geopy import distance, Point

from ._utilities import (plot_basemap,
                         save_map,
                         mapviz,
                         _load_and_validate,
                         get_max_extent,
                         save_animated_map)


def geodesic_distance(metadata: qiime2.Metadata,
                      latitude: str = 'Latitude',
                      longitude: str = 'Longitude',
                      missing_data: str = 'error') -> DistanceMatrix:
    sample_md = _load_and_validate(
        metadata, [latitude, longitude], ['latitude', 'longitude'],
        missing_data=missing_data)

    # Collect geocoordinate points
    points = [Point(x) for x in zip(sample_md[latitude], sample_md[longitude])]

    # Compute pairwise distances between all points
    def distance_function(a, b):
        return distance.geodesic(a, b).meters

    dm = DistanceMatrix.from_iterable(
        points, metric=distance_function, keys=sample_md.index)

    return dm


def euclidean_distance(metadata: qiime2.Metadata,
                       x: str,
                       y: str,
                       z: str = None,
                       missing_data: str = 'error') -> DistanceMatrix:
    cols = [x, y]
    names = ['x', 'y']
    if z is not None:
        cols.append(z)
        names.append('z')

    sample_md = _load_and_validate(metadata, cols, names, missing_data)

    # Compute pairwise distances between all points
    distances = scipy.spatial.distance.pdist(
        sample_md.values, metric='euclidean')

    dm = DistanceMatrix(distances, ids=sample_md.index)

    return dm


def draw_map(output_dir: str,
             metadata: qiime2.Metadata,
             column: str = None,
             latitude: str = 'Latitude',
             longitude: str = 'Longitude',
             image: str = 'StamenTerrain',
             color_palette: str = 'rainbow',
             discrete: bool = False,
             missing_data: str = 'error'):
    metadata = _load_and_validate(
        metadata, [column, latitude, longitude],
        ['column', 'latitude', 'longitude'], missing_data)

    # set up basemap
    ax, cmap = plot_basemap(
        metadata[latitude], metadata[longitude], image, color_palette)

    # plot coordinates on map. If column is numeric, color points by column
    if np.issubdtype(metadata[column].dtype, np.number) and not discrete:
        metadata[column] = metadata[column].astype(float)
        plt.scatter(metadata[longitude], metadata[latitude],
                    c=list(metadata[column]), transform=ccrs.Geodetic(),
                    cmap=cmap)
        # set up a colorbar
        normalize = mcolors.Normalize(
            vmin=metadata[column].min(), vmax=metadata[column].max())
        scalarmappaple = cm.ScalarMappable(norm=normalize, cmap=cmap)
        scalarmappaple.set_array(metadata[column])
        plt.colorbar(scalarmappaple).set_label(column)
    # if column is not numeric, color discretely
    else:
        groups = metadata[column].unique()
        colors = cmap(np.linspace(0, 1, len(groups)))
        for group, c in zip(groups, colors):
            # Note that this assumes this will always be metadata; alpha
            # diversity values should always be numeric.
            subset = metadata[metadata[column] == group]
            plt.plot(subset[longitude], subset[latitude], 'o', color=c,
                     transform=ccrs.Geodetic())
        ax.legend(groups, bbox_to_anchor=(1.05, 1))

    save_map(ax, output_dir)
    mapviz(output_dir)


def draw_interactive_map(output_dir: str,
                         metadata: qiime2.Metadata,
                         column: str = None,
                         latitude: str = 'Latitude',
                         longitude: str = 'Longitude',
                         color_palette: str = 'rainbow',
                         discrete: bool = False,
                         missing_data: str = 'error'):

    metadata = _load_and_validate(
        metadata, [column, latitude, longitude],
        ['column', 'latitude', 'longitude'], missing_data)

    lat_0, lat_1, lon_0, lon_1 = get_max_extent(
        metadata[latitude], metadata[longitude])
    loc_min, loc_max = [lon_0, lat_0], [lon_1, lat_1]

    cmap = plt.get_cmap(color_palette)

    data = []
    # If column is numeric, color points by column
    if np.issubdtype(metadata[column].dtype, np.number) and not discrete:
        metadata[column] = metadata[column].astype(float)
        normalize = mcolors.Normalize(
            vmin=metadata[column].min(), vmax=metadata[column].max())
        scalarmappaple = cm.ScalarMappable(
            norm=normalize, cmap=cmap)
        scalarmappaple.set_array(metadata[column])

        fig, ax = plt.subplots()
        plt.colorbar(scalarmappaple).set_label(column)
        ax.remove()

        metadata.sort_values(by=column, ascending=False, inplace=True)
        for i, row in metadata.iterrows():
            data.append({
                'sample_id': i,
                column: row[column],
                'latitude': row[latitude],
                'longitude': row[longitude],
                'color': mcolors.to_hex(scalarmappaple.to_rgba(row[column]))
            })
    # if column is not numeric, color discretely
    else:
        groups = metadata[column].unique()
        len_groups = len(groups)
        colors = {g: mcolors.to_hex(c) for g, c in zip(
            groups, cmap(np.linspace(0, 1, len(groups))))}

        for i, row in metadata.iterrows():
            data.append({
                'sample_id': i,
                column: row[column],
                'latitude': row[latitude],
                'longitude': row[longitude],
                'color': colors[row[column]]
            })

        fig = plt.figure(figsize=[len_groups * 0.05, len_groups/2])
        ax = fig.add_axes([0, 0, 1, 1])

        for idx, (g, color) in enumerate(colors.items()):
            r = mpatch.Rectangle((0, idx), 1, 1, color=color)
            _ = ax.text(2, idx+.5, '  %s' % g, va='center', fontsize=10)
            ax.add_patch(r)
            ax.axhline(idx, color='k')
        ax.set_xlim(0, 3)
        ax.set_ylim(0, idx + 2)
        ax.axis('off')

    save_animated_map(output_dir, loc_min, loc_max, data, column)
