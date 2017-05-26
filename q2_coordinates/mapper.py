#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2017--, q2-coordinates development team.
#
# Distributed under the terms of the Lesser GPL 3.0 licence.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.cm as cm
import numpy as np
import pandas as pd
import matplotlib.colors as mcolors
import qiime2
from q2_sample_classifier.utilities import metadata_to_df

from ._utilities import (get_map_params, get_max_extent, plot_basemap,
                         save_map, mapviz)


def map_predicted_coordinates(output_dir: str,
                              predictions: pd.DataFrame,
                              prediction_regression: pd.DataFrame,
                              metadata: qiime2.Metadata,
                              latitude: str='Latitude',
                              longitude: str='Longitude',
                              pred_lat: str='Latitude',
                              pred_long: str='Longitude',
                              image: str='StamenTerrain'):

    # Load metadata, attempt to convert to numeric
    metadata = metadata_to_df(metadata)
    predictions = predictions.apply(
        lambda x: pd.to_numeric(x, errors='ignore'))

    # set up basemap
    ax, cmap = plot_basemap(predictions[pred_lat].append(metadata[latitude]),
                            predictions[pred_long].append(metadata[longitude]),
                            image)

    print(metadata[longitude])
    print(predictions[pred_long])
    print(metadata[latitude])
    print(predictions[pred_lat])
    print(type(metadata[longitude]), type(predictions[pred_long]))
    # plot all actual coordinates
    plt.plot(metadata[longitude], metadata[latitude], 'o', color='black',
             transform=ccrs.Geodetic())

    # plot actual test coordinates
    metadata = metadata.loc[predictions.index]
    plt.plot(metadata[longitude], metadata[latitude], 'o', color='b',
             transform=ccrs.Geodetic())

    # plot predicted coordinates
    plt.plot(predictions[pred_lat], predictions[pred_long], 'o', color='r',
             alpha=0.8, transform=ccrs.Geodetic())
    ax.legend(
        ['training set', 'actual', 'predicted'], bbox_to_anchor=(1.05, 1))

    save_map(ax, output_dir)
    mapviz(output_dir, prediction_regression)


def map_metadata_coordinates(output_dir: str,
                             alpha_diversity: pd.Series,
                             metadata: qiime2.Metadata,
                             category: str=None,
                             latitude: str='Latitude',
                             longitude: str='Longitude',
                             image: str='StamenTerrain',
                             color_palette: str='rainbow',
                             discrete: bool=False):

    # Load metadata, attempt to convert to numeric
    metadata = metadata_to_df(metadata)
    alpha_diversity = alpha_diversity.convert_objects(convert_numeric=True)

    # set up basemap
    ax, cmap = plot_basemap(
        metadata[latitude], metadata[longitude], image, color_palette)

    # determine whether to color by metadata or alpha_diversity
    if category in metadata:
        pass
    elif alpha_diversity is not None:
        category = alpha_diversity.name
        metadata = metadata.merge(
            pd.DataFrame(alpha_diversity), left_index=True, right_index=True)
    else:
        raise ValueError((
            'Must define metadata category or alpha diversity artifact to '
            'use for sample coloring. "category" is not found in "metadata". '
            'Please check your inputs and supply a valid "category" or alpha '
            'diversity artifact to use for coloring.'))

    # plot coordinates on map. If category is numeric, color points by category
    if np.issubdtype(metadata[category].dtype, np.number) and not discrete:
        metadata[category] = metadata[category].astype(float)
        print(metadata[category])
        plt.scatter(metadata[longitude], metadata[latitude],
                    c=list(metadata[category]), transform=ccrs.Geodetic(), cmap=cmap)
        # set up a colorbar
        normalize = mcolors.Normalize(
            vmin=metadata[category].min(), vmax=metadata[category].max())
        scalarmappaple = cm.ScalarMappable(norm=normalize, cmap=cmap)
        scalarmappaple.set_array(metadata[category])
        plt.colorbar(scalarmappaple).set_label(category)
    # if category is not numeric, color discretely
    else:
        groups = metadata[category].unique()
        colors = cmap(np.linspace(0, 1, len(groups)))
        for group, c in zip(groups, colors):
            # Note that this assumes this will always be metadata; alpha
            # diversity values should always be numeric.
            subset = metadata[metadata[category] == group]
            plt.plot(subset[longitude], subset[latitude], 'o', color=c,
                     transform=ccrs.Geodetic())
        ax.legend(groups, bbox_to_anchor=(1.05, 1))

    save_map(ax, output_dir)
    mapviz(output_dir)
