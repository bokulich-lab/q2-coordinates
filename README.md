# q2-coordinates

[![Build Status](https://travis-ci.org/nbokulich/q2-coordinates.svg?branch=master)](https://travis-ci.org/nbokulich/q2-coordinates) [![Coverage Status](https://coveralls.io/repos/github/nbokulich/q2-coordinates/badge.svg?branch=master)](https://coveralls.io/github/nbokulich/q2-coordinates?branch=master) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2124295.svg)](https://doi.org/10.5281/zenodo.2124295)


A qiime2 plugin supporting methods for geographic mapping of qiime2 artifact data or metadata. 

Quadtree functionality allows the user to objectively partition a dataset based on x and y coordinate information (for example, longitude and latitude).

Quadtree functionality allows the user to objectively partition a dataset based on x and y coordinate information (for example, longitude and latitude).

q2-coordinates makes it easy to plot geographic coordinates and associated (meta)data on beautiful topographic, street maps or interactive geographical maps.

Map tiling, resolution calculation, and coordinate projection occur automatically. All the user needs to do is input a two-dimensional list of geocoordinates to plot, in decimal degrees, as shown in the examples below.

Currently, StamenTerrain, Open Street Maps, Google Maps and OpenLayers are supported, producing high-quality maps from anywhere on planet Earth.

Map projections are quick for small maps, but may take several minutes for very large maps (e.g., trans-continental).

# Install
We recommend using the functonalities in a conda environment with the required dependencies installed within:
```
conda create -y -n q2coord
conda activate q2coord

conda install \
  -c conda-forge -c bioconda -c qiime2 -c defaults \
  qiime2 q2cli q2templates q2-types q2-diversity scikit-bio "pysal==2.0" geopy numpy "cartopy==0.16" scipy \
  "matplotlib=3.2" pandas biom-format dill
```
Now install q2-coordinates:
```
pip install git+https://github.com/nbokulich/q2-coordinates.git
```
To avoid warnings about geopandas you can additionally install it as:
```
pip install geopandas
```

# Examples
In the examples below we will use some bacterial 16S rRNA gene amplicon sequence data collected from Californian vineyards, as described by [Bokulich et al. 2016](https://doi.org/10.1128/mBio.00631-16). 😎🍷

## Plotting geocoordinates colored by alpha diversity values
This visualizer takes a SampleData[AlphaDiversity] artifact and sample metadata TSV as input, and plots sample coordinates on the built-in maps. Sample points are colored as a function of alpha diversity values.

Clone into repository and get access to the test data:
```
git clone https://github.com/nbokulich/q2-coordinates.git

cd q2-coordinates/q2_coordinates/tests/data/
```
Draw map of alpha diversity values:
```
qiime diversity alpha \
    --i-table even_table.qza \
    --p-metric observed_features \
    --o-alpha-diversity alpha_diversity_sample.qza

qiime coordinates draw-map \
    --m-metadata-file alpha_diversity_sample.qza \
    --m-metadata-file chardonnay_sample_metadata.txt \
    --p-latitude latitude \
    --p-longitude longitude \
    --p-column observed_features \
    --o-visualization diversity-map.qzv
```

![Alt text](./examples/alpha-diversity.jpg?raw=true "coordinates colored by observed species")

Draw interactive map of alpha diversity values:
```
qiime coordinates draw-interactive-map \
    --m-metadata-file alpha_diversity_sample.qza \
    --m-metadata-file chardonnay_sample_metadata.txt \
    --p-latitude latitude \
    --p-longitude longitude \
    --p-column observed_features \
    --o-visualization diversity-interactive-map.qzv
```

Note that _any_ metadata-transformable artifacts can be used as a `metadata-file` input to this command, so this opens the door to many other data types, e.g., PCoA results, predictions, etc.

HINT: If you are not sure what the `column` name is for your artifact of interest, use `qiime tools inspect-metadata` to see the available column names.

## Plotting geocoordinates colored by metadata category values
We can use the same visualizer action for plotting alpha diversity values to color sample points as a function of continuous or categorical sample metadata. To do this, we simply add the "category" parameter to use that category from the sample metadata instead of alpha diversity values. The plot below shows the various vineyard sites (indicated by anonymous numbers) where samples were collected.
```
qiime coordinates draw-map \
    --m-metadata-file chardonnay_sample_metadata.txt \
    --p-column vineyard \
    --p-latitude latitude \
    --p-longitude longitude \
    --p-discrete \
    --o-visualization vineyard-map.qzv
```
![Alt text](./examples/vineyard-map.jpg?raw=true "coordinates colored by metadata values")

## Converting (geo)coordinates to a distance matrix
This is a cinch with q2-coordinates! To calculate geodesic distance from geocoordinate data, use the `geodesic-distance` method:
```
qiime coordinates geodesic-distance \
    --m-metadata-file chardonnay_sample_metadata.txt \
    --p-latitude latitude \
    --p-longitude longitude \
    --o-distance-matrix geodesic_distance_matrix_sample.qza
```

This computes geodesic distance (in meters) between each point. Note that samples with missing values are ignored.

We can also construct a distance matrix from 2D or 3D spatial coordinates using the `euclidean-distance` method:
```
qiime coordinates euclidean-distance \
    --m-metadata-file xyz-coordinates.tsv \
    --p-x x \
    --p-y y \
    --p-z z \
    --o-distance-matrix xyz_distance_matrix_sample.qza
```

We can use these distance matrices for other useful QIIME 2 methods, e.g., to compute a mantel test comparing two different distance matrices. For example, we can compare Bray-Curtis dissimilarities between microbial communities to geospatial distances between our vineyard samples:
```
qiime diversity beta \
    --i-table even_table.qza \
    --p-metric braycurtis \
    --o-distance-matrix bray_curtis_distance_sample.qza

qiime diversity mantel \
    --i-dm1 geodesic_distance_matrix_sample.qza \
    --i-dm2 bray_curtis_distance_sample.qza \
    --p-intersect-ids \
    --o-visualization mantel_sample.qzv
```

## Computing autocorrelation statistics
Spatial autocorrelation measures the similarity of a measurement taken across space. Correlations can be either positive, which indicates similar values in adjacent spaces, or negative, which indicates that dissimilar measurements are evenly arranged across space. In both cases, autocorrelation indicates that the observed pattern is non-random. We can compute [Moran's I](https://en.wikipedia.org/wiki/Moran%27s_I) and [Geary's C](https://en.wikipedia.org/wiki/Geary%27s_C) autocorrelation tests based on a spatial distance matrix using the `autocorr` visualizer.
```
qiime coordinates autocorr \
    --i-distance-matrix geodesic_distance_matrix_sample.qza \
    --m-metadata-file alpha_diversity_sample.qza \
    --m-metadata-column observed_features \
    --p-intersect-ids \
    --o-visualization autocorrelation_sample.qzv
```

Moran's I ranges from -1 (negative spatial autocorrelation) to 1 (positive spatial autocorrelation); values near 0 or the expected I (EI, which approaches 0 with large sample sizes) indicate a random spatial distribution. Geary's C ranges from 0 (positive spatial autocorrelation) to some unspecified value greater than 1 (negative spatial autocorrelation); values near 1 indicate a random distribution. Both are global autocorrelation tests, though Geary's C is much more sensitive to local autocorrelation processes. The accompanying Moran plot shows the relationship between the variable of interest and its own spatial lag (i.e., the degree to which neighboring observations are autocorrelated).

## Using quadtrees
The quadtree function splits the region of points into bins recursively based on a threshold. If the number of samples in a section is larger than the threshold they will split into four, allowing detailed use, description, and partitioning of space based on sample density.

```
qiime coordinates quadtree \
    --m-metadata-file chardonnay_sample_metadata.txt \
    --p-y-coord latitude \
    --p-x-coord longitude \
    --p-threshold 50 \
    --output-dir test
```

### Visualizing quadtrees
Quadtrees can easily be visualized using a mix of python and other existing qiime2 plugins. Some ideas include:
1. using q2-coordinates draw map to display the sample positions and color code them by respective quadrant (i.e: set the "column" parameter to the split-depth you want to look at)
2. using q2-empress to view and navigate the tree to see number and size of splits. This requires the installation of the qiime2 empress plugin:https://github.com/biocore/empress.

```
using qiime2 cli
    qiime empress tree-plot \
    --i-tree test/output_tree.qza \
    --m-feature-metadata-file chardonnay_sample_metadata.txt \
    --output-dir empress
```

# License
q2-coordinates is released under a BSD-3-Clause license. See LICENSE for more details.
