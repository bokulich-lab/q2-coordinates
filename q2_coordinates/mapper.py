#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2017--, QIIME 2 development team.
#
# Distributed under the terms of the Lesser GPL 3.0 licence.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.cm as cm
import numpy as np
import matplotlib.colors as mcolors
import qiime2

from skbio import DistanceMatrix
from geopy import distance, Point

from ._utilities import (plot_basemap,
                         save_map,
                         mapviz,
                         _load_and_validate,
                         _validate_columns)


def distance_matrix(metadata: qiime2.Metadata,
                    latitude: str='Latitude',
                    longitude: str='Longitude') -> DistanceMatrix:

    sample_md = _load_and_validate(
        metadata, [latitude, longitude], ['latitude', 'longitude'])

    # Collect geocoordinate points
    points = [Point(x) for x in zip(sample_md[latitude], sample_md[longitude])]

    # Compute pairwise distances between all points
    def distance_function(a, b):
        return distance.geodesic(a, b).meters

    dm = DistanceMatrix.from_iterable(
        points, metric=distance_function, keys=sample_md.index)

    return dm


def draw_map(output_dir: str,
             metadata: qiime2.Metadata,
             column: str=None,
             latitude: str='Latitude',
             longitude: str='Longitude',
             image: str='StamenTerrain',
             color_palette: str='rainbow',
             discrete: bool=False):

    metadata = _load_and_validate(
        metadata, [column, latitude, longitude],
        ['column', 'latitude', 'longitude'])

    # set up basemap
    ax, cmap = plot_basemap(
        metadata[latitude], metadata[longitude], image, color_palette)

    # plot coordinates on map. If column is numeric, color points by column
    if np.issubdtype(metadata[column].dtype, np.number) and not discrete:
        metadata[column] = metadata[column].astype(float)
        print(metadata[column])
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
