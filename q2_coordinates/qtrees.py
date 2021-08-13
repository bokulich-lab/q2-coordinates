# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
import skbio
import qiime2
from functools import partial


def clean(metadata, y_coord, x_coord):

    if y_coord not in metadata:
        raise ValueError("Must have y_coord in metadata to use quadtrees")

    if x_coord not in metadata:
        raise ValueError("Must have x_coord in metadata to use quadtrees")

    df = metadata[[x_coord, y_coord]]

    # as global or local in function, define all null or this:
    df[y_coord] = pd.to_numeric(df[y_coord], errors='coerce')
    df[x_coord] = pd.to_numeric(df[x_coord], errors='coerce')

    # drop nan values (formerly strings) from dataframe
    df = df.dropna(subset=[x_coord, y_coord])

    if df.empty is True:
        raise ValueError("x coordinates and/or y coordinates have "
                         "no numeric values, please check your data.")
    # resolve points shifted left or down
    xmin = df[x_coord].min()
    if xmin > 0:
        df[x_coord] = df[x_coord] - xmin
        xmin = 0

    ymin = df[y_coord].min()
    if ymin > 0:
        df[y_coord] = df[y_coord] - ymin
        ymin = 0

    df[x_coord] = df[x_coord] - xmin
    df[y_coord] = df[y_coord] - ymin
    return df


class Point():
    def __init__(self, x, y, sample_id):
        self.x = float(x)
        self.y = float(y)
        self.sample_id = sample_id


class Node():
    def __init__(self, x0, y0, w, h, points, _id):
        self.x0 = x0
        self.y0 = y0
        self.width = float(w)
        self.height = float(h)
        self.points = points
        self.children = []
        self.id = _id

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_points(self):
        return self.points

    def get_id(self):
        return self.id

    def set_id(self, _id):
        self.id = self.id+_id


class QTree():
    def __init__(self, threshold, data):
        self.threshold = threshold
        self.points = [Point(x, y, sample_id) for sample_id, x, y in data]
        x_max = max(x for _, x, _ in data)
        y_max = max(y for _, _, y in data)
        self.root = Node(0, 0, x_max, y_max, self.points, "0")

    def add_point(self, x, y, sample_id):
        self.points.append(Point(x, y, sample_id))

    def get_points(self):
        return self.points

    def subdivide(self, threshold):
        depth = 0
        node_id = ""
        bins = []
        bins = recursive_subdivide(self.root, threshold, depth, node_id, bins)
        return bins


def recursive_subdivide(node, k, depth, node_id, bins):
    if len(node.points) < k:
        return
    elif len(node.points)/k >= len(node.points):
        raise ValueError("The threshold for subdivision is less than "
                         "the amount of points, "
                         "please chose a larger threshold for division")
    w_ = node.width/2
    h_ = node.height/2
    depth += 1
    nodes = []
    for i in range(4):
        # northwest
        if(i == 0):
            quad = "1"
            node.x0 = node.x0
            node.y0 = node.y0+h_
        # northeast
        elif(i == 1):
            quad = "2"
            node.x0 = node.x0+w_
            node.y0 = node.y0
        # southwest
        elif(i == 2):
            quad = "3"
            node.x0 = node.x0-w_
            node.y0 = node.y0-h_
        # southeast
        elif(i == 3):
            quad = "4"
            node.x0 = node.x0+w_
            node.y0 = node.y0

        p = contains(node.x0, node.y0, w_, h_, node.points)
        new_id = node_id + quad + "."
        quad_node = Node(node.x0, node.y0, w_, h_, p, new_id)
        nodes.append(quad_node)

        for pt in p:
            bins.append((pt.sample_id, depth, new_id))

        recursive_subdivide(quad_node, k, depth, new_id, bins)
    node.children = nodes
    return bins


def contains(x, y, w, h, points):
    pts = []
    for point in points:
        if point.x >= x and point.x <= x+w and point.y >= y and point.y <= y+h:
            pts.append(point)
    return pts


def create_tree_df(bins, index):
    # create df for trees and df
    df = pd.DataFrame(bins, columns=[index, 'depth', 'lineage'])
    try:
        max_depth = max([lineage.count('.') for lineage in df['lineage']])+1
    except ValueError:
        raise ValueError("The threshold for subdivision is greater than "
                         "the amount of samples, "
                         "please chose a smaller threshold for division")

    # for df only
    def lineage_chopper(depth, lineage):
        lin = '.'.join(lineage.split('.', depth)[:depth])
        if lineage.count('.') < depth:
            lin = None
        return lin

    for depth in range(1, max_depth):
        name = 'split-depth-%d' % depth
        df[name] = df['lineage'].apply(partial(lineage_chopper, depth))

    # tree and df
    longest_lineages = []
    for sample_id, sample_grp in df.groupby(index):
        sample_grp_sorted = sample_grp.sort_values('depth', ascending=False)
        longest_lineages.append(sample_grp_sorted.iloc[0])
    longest_lineages = pd.DataFrame(longest_lineages)
    # tree only
    lineage_bit = longest_lineages['lineage'].apply(
        lambda lin: lin.split('.')[:-1])
    taxonomy = [(i, lin) for i, lin in zip(longest_lineages[index],
                                           lineage_bit)]
    # df formatting
    longest_lineages = pd.DataFrame(longest_lineages).set_index(index)
    longest_lineages.index.name = index
    trees = skbio.TreeNode.from_taxonomy(taxonomy)

    # to allow plotting in q2-empress node lenght must be > 0,
    # so set arbitrary node length
    for node in trees.traverse():
        if node.length is None:
            node.length = 1.0
    return trees, longest_lineages


def get_results(cleaned_df, threshold, index):
    cleaned_df = cleaned_df.reset_index()
    xy = cleaned_df.to_numpy()
    q = QTree(threshold, xy)
    bins = q.subdivide(threshold)
    tree, samples = create_tree_df(bins, index)
    return tree, samples


def quadtree(metadata: qiime2.Metadata,
             y_coord: str,
             x_coord: str,
             threshold: int) -> (skbio.TreeNode, pd.DataFrame):
    metadata = metadata.to_dataframe()
    index = metadata.index.name
    cleaned_df = clean(metadata, y_coord, x_coord)
    tree, samples = get_results(cleaned_df, threshold, index)
    return tree, samples
