#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2017--, QIIME 2 development team.
#
# Distributed under the terms of the Lesser GPL 3.0 licence.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import matplotlib.pyplot as plt
import qiime2
from pysal.explore.esda import geary, moran
from pysal.lib import weights as psw
import pandas as pd
from skbio import DistanceMatrix
import seaborn as sns
from ._utilities import save_map, mapviz


def autocorr(output_dir: str,
             distance_matrix: DistanceMatrix,
             metadata: qiime2.NumericMetadataColumn,
             permutations: int=999,
             two_tailed: bool=True,
             transformation: str='R',
             intersect_ids: bool=False) -> None:

    # match ids — metadata can be superset
    metadata = metadata.to_series()
    metadata, distance_matrix = match_ids(
        metadata, distance_matrix, intersect_ids=intersect_ids)

    # compute Moran's I and Geary's class
    results, weights = autocorr_from_dm(metadata,
                                        distance_matrix,
                                        permutations=permutations,
                                        two_tailed=two_tailed,
                                        transformation=transformation)

    mplot = moran_plot(metadata, weights, transformation)

    # Visualize
    save_map(mplot, output_dir)
    mapviz(output_dir, results=results, title='Autocorrelation statistics')


def match_ids(metadata, distance_matrix, intersect_ids):
    dm_ids = distance_matrix.ids
    metadata = metadata.filter(dm_ids)
    md_ids = metadata.index
    if len(md_ids) == 0:
        raise ValueError(
            'No samples match between distance matrix and metadata')
    if not intersect_ids:
        missing_ids = set(dm_ids).difference(md_ids)
        if len(missing_ids) > 0:
            raise ValueError(
                'Samples found in the distance matrix are missing from the '
                'sample metadata. You can use the intersect_ids parameter '
                'to ignore this message if missing values do not impact '
                'pairwise distances. Missing IDs: {0}'.format(missing_ids))
    else:
        distance_matrix = distance_matrix.filter(ids=md_ids)
    return metadata, distance_matrix


def moran_plot(metadata, weights, transformation):
    # standardize (center) metadata values
    std_y = (metadata - metadata.mean()) / metadata.std()
    # perform designated transformation of weights matrix
    weights.transform = transformation
    # compute spatial lag
    _spatial_lag = psw.spatial_lag.lag_spatial(weights, std_y)
    # draw Moran plot
    sns.set_style("whitegrid")
    mplot = sns.regplot(x=std_y, y=_spatial_lag, color='grey')
    plt.axvline(0, c='black', alpha=0.25)
    plt.axhline(0, c='black', alpha=0.25)
    plt.ylabel('Spatial Lag')
    plt.xlabel('Normalized {0}'.format(metadata.name))

    return mplot


def autocorr_from_dm(metadata, distance_matrix, permutations, two_tailed,
                     transformation):

    # convert distance_matrix to weights matrix
    weights = psw.util.full2W(distance_matrix.data, ids=distance_matrix.ids)

    # Compute autocorrelation stats
    mi = moran.Moran(metadata, weights, permutations=permutations,
                     two_tailed=two_tailed, transformation=transformation)

    gc = geary.Geary(metadata, weights, permutations=permutations,
                     transformation=transformation)

    names = ['Test Statistic', 'Expected Value', 'Z norm', 'p norm']
    moran_res = [mi.I, mi.EI, mi.z_norm, mi.p_norm]
    geary_res = [gc.C, gc.EC, gc.z_norm, gc.p_norm]
    if permutations > 0:
        names.extend(
            ['Permuted Avg Test Statistic', 'Z simulated', 'p simulated'])
        moran_res.extend([mi.EI_sim, mi.z_sim, mi.p_sim])
        geary_res.extend([gc.EC_sim, gc.z_sim, gc.p_sim])

    results = pd.DataFrame(
        {'Moran\'s I': moran_res, 'Geary\'s C': geary_res}, index=names)
    return results, weights
