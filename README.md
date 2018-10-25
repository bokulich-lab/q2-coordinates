# q2-coordinates
A qiime2 plugin supporting methods for geographic mapping of qiime2 artifact data or metadata.

q2-coordinates makes it easy to plot geographic coordinates and associated (meta)data on beautiful topographic and street maps.

Map tiling, resolution calculation, and coordinate projection occur automatically. All the user needs to do is input a two-dimensional list of geocoordinates to plot, in decimal degrees, as shown in the examples below.

Currently, StamenTerrain, Open Street Maps, and Google Maps are supported, producing high-quality maps from anywhere on planet Earth.

Map projections are quick for small maps, but may take several minutes for very large maps (e.g., trans-continental).

# Examples
## Plotting geocoordinates colored by alpha diversity values
This visualizer takes a SampleData[AlphaDiversity] artifact and sample metadata TSV as input, and plots sample coordinates on the built-in maps. Sample points are colored as a function of alpha diversity values.
```
cd ~/Desktop/projects/q2-coordinates/q2_coordinates/test_data/

qiime diversity alpha --i-table even_table.qza --p-metric observed_otus --o-alpha-diversity alpha_diversity
qiime coordinates map-metadata-coordinates --i-alpha-diversity alpha_diversity.qza --m-metadata-file chardonnay.map.txt --p-latitude latitude --p-longitude longitude --o-visualization diversity-map
```
![Alt text](./examples/alpha-diversity.jpg?raw=true "coordinates colored by observed species")

## Plotting geocoordinates colored by metadata category values
We can use the same visualizer action for plotting alpha diversity values to color sample points as a function of continuous or categorical sample metadata. To do this, we simply add the "category" parameter to use that category from the sample metadata instead of alpha diversity values (which must still be input for the time being, until qiime2 permits optional artifacts). The plot below shows the various vineyard sites (indicated by anonymous numbers) where samples were collected.
```
qiime coordinates map-metadata-coordinates --i-alpha-diversity alpha_diversity.qza --m-metadata-file chardonnay.map.txt --p-category vineyard --p-latitude latitude --p-longitude longitude --o-visualization vineyard-map --p-discrete
```
![Alt text](./examples/vineyard-map.jpg?raw=true "coordinates colored by metadata values")
