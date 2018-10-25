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

from ._utilities import (plot_basemap, save_map, mapviz)


def draw_map(output_dir: str,
             metadata: qiime2.Metadata,
             column: str=None,
             latitude: str='Latitude',
             longitude: str='Longitude',
             image: str='StamenTerrain',
             color_palette: str='rainbow',
             discrete: bool=False):

    # Load metadata
    metadata = metadata.to_dataframe()

    # set up basemap
    ax, cmap = plot_basemap(
        metadata[latitude], metadata[longitude], image, color_palette)

    # validate sample metadata columns
    cs = [(column, 'column'), (latitude, 'latitude'), (longitude, 'longitude')]
    for c, name in cs:
        if c in metadata:
            pass
        else:
            raise ValueError(
                'Must define a valid "{0}" column to use for sample mapping. '
                '"{1}" is not a valid column name in your sample metadata '
                'file.'.format(name, c))

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
