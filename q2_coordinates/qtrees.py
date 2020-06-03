#!/usr/bin/env python
# coding: utf-8


import biom
import pandas as pd
import numpy as np
import skbio
import qiime2
def clean(metadata, latitude, longitude, index):
    if latitude not in metadata: #and selected method of binning
        raise ValueError("Must have latitude in metadata to use quadtrees")
    if longitude not in metadata: #and selected method of binning
        raise ValueError("Must have longitude in metadata to use quadtrees")
    

    ## if selected method of binning is mock
    #md_edited['country'] = md_df['country']

    df = metadata[['longitude','latitude']]

    #as global or local in function, define all null or this:
    df[latitude] = pd.to_numeric(df.latitude, errors='coerce')
    df[longitude] = pd.to_numeric(df.longitude, errors='coerce')
    
    #drop nan values (formerly strings) from dataframe
    df = df.dropna(subset = [longitude, latitude])
  
    if df.empty is True:
        raise ValueError("Latitude and/or Longitude have no numeric values, please check your data.")

    #check if latitude and longitude is castable as float
    df[latitude] = df[latitude].astype(float)
    df[longitude] = df[longitude].astype(float)

    #make (0,0) be the bottom right corner for ease of calculation, probably a better way to do this?
    df[latitude] = df[latitude] + 90
    df[longitude] = df[longitude] + 180
    
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
    def __init__(self, k, data):
        self.threshold = k
        self.points = [Point(x, y, sample_id) for sample_id, x, y in data]
        self.root = Node(0, 0, 360, 180, self.points, "0")

    def add_point(x, y, sample_id):
        self.points.append(Point(x, y, sample_id))
    
    def get_points(self):
        return self.points
    
    def subdivide(self, samples, threshold):
        count = 0
        node_id = ""
        samples = samples
        bins  = []
        
        samples, bins = recursive_subdivide(self.root, threshold, count, node_id, samples, bins)
        return samples, bins
    

def recursive_subdivide(node, k, count, node_id, samples, bins):

    if len(node.points) < k:
        return
    elif len(node.points)/k >= len(node.points):
        raise ValueError("The threshold for subdivision is less than the amount of points in one place,", 
                         "please chose a larger threshold for division")
    else:
        count += 1

    samples["H" + str(count)] = ""
    
    w_ = node.width/2
    h_ = node.height/2    
    
    nodes = []
    sk_nodes = []
    for i in range(4):
        #southwest
        if(i ==0):
            quad = "3"
            node.x0 = node.x0
            node.y0 = node.y0
        #northwest
        elif(i==1):
            quad = "1"
            node.x0 = node.x0
            node.y0 = node.y0+h_
        #northeast
        elif(i == 2):
            quad = "2"
            node.x0 = node.x0+w_
            node.y0 = node.y0
        #southeast
        elif(i == 3):
            quad = "4"
            node.x0 = node.x0
            node.y0 = node.y0-h_

        p = contains(node.x0, node.y0, w_, h_, node.points)
        quad_node= Node(node.x0, node.y0, w_, h_, p, node_id+quad+".")
        
        for pt in p:
            bins.append((pt.sample_id, count, quad_node.get_id()))
        
        nodes.append(quad_node)
        recursive_subdivide(quad_node, k, count, node_id+quad+".", samples, bins)
        

    node.children = nodes
    return samples, bins

    #if number of input samples/k is less than 4 there may be issues raise exception
    
    
def contains(x, y, w, h, points):
    pts = []
    for point in points:
        if point.x >= x and point.x <= x+w and point.y>=y and point.y<=y+h:
            pts.append(point)
    return pts

def create_tree(samples):
    tree = skbio.TreeNode(name="root")
    lineages = []
    for i in samples.iterrows():
        values = list(i[1])
        
        lineages.append((i[0], values))

    tree.extend(skbio.TreeNode.from_taxonomy(lineages))
    return tree

def create_sample_df(bins, samples, index):
    print(samples.head())
    print(index)
    for samp, bin_i, items in bins:
        bin_name = "H" + str(bin_i)
        print(samples[index])
        samples[bin_name] = np.where(samples[index] == samp, items, samples[bin_name])
    return samples

def get_results(cleaned_df, threshold, index):
    cleaned_df = cleaned_df.reset_index()
    xy = cleaned_df.to_numpy()
    q = QTree(threshold, xy)
    samples = pd.DataFrame()
    samples[index] = cleaned_df[index]
    samples = samples.set_index(index)
    samples, bins = q.subdivide(samples, threshold)
    samples = samples.reset_index()
    samples = create_sample_df(bins, samples, index)
    samples = samples.set_index(index)

    tree = create_tree(samples)

    return tree, samples

def quadtree(metadata:qiime2.Metadata, 
             latitude: str, 
             longitude:str,
             threshold:int) -> (skbio.TreeNode, pd.DataFrame):
    metadata = metadata.to_dataframe()
    index = metadata.index.name
    cleaned_df = clean(metadata, latitude, longitude, index)
    tree, samples = get_results(cleaned_df,threshold, index)

    return tree, samples
