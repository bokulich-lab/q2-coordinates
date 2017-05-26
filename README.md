# q2-coordinates
methods for geographic mapping of qiime2 artifact data or metadata

# Examples
## Plotting geocoordinates colored by alpha diversity values
![Alt text](./examples/alpha-diversity.pdf?raw=true "coordinates colored by observed species")
```
cd ~/Desktop/projects/q2-coordinates/q2_coordinates/test_data/

qiime diversity alpha --i-table even_table.qza --p-metric observed_otus --o-alpha-diversity alpha_diversity
qiime coordinates map-metadata-coordinates --i-alpha-diversity alpha_diversity.qza --m-metadata-file chardonnay.map.txt --p-latitude latitude --p-longitude longitude --o-visualization diversity-map
```
## Plotting geocoordinates colored by metadata category values
![Alt text](./examples/vineyard-map.pdf?raw=true "coordinates colored by metadata values")
This uses the same visualizer as for plotting alpha diversity values, but we add the "category" parameter to use that category from the sample metadata instead of alpha diversity values.
```
qiime coordinates map-metadata-coordinates --i-alpha-diversity alpha_diversity.qza --m-metadata-file chardonnay.map.txt --p-category vineyard --p-latitude latitude --p-longitude longitude --o-visualization vineyard-map --p-discrete
```
## Plotting predicted vs. expected geocoordinates
![Alt text](./examples/predicted-coordinates.pdf?raw=true "predicted and observed coordinates")
q2-sample-classifier predict-coordinates allows us to predict two continuous variables on a single set of test data, allowing us to determine how well microbial composition predicts geographical source.
```
qiime sample-classifier predict-coordinates --i-table chardonnay.table.qza --m-metadata-file chardonnay.map.txt --p-latitude latitude --p-longitude longitude --p-n-jobs 4 --o-predictions coord-predictions --o-prediction-regression coord-regression
```
This method generates a list of predicted latitude and longitude coordinates for each sample, contained in the 'predictions' artifact. The 'accuracy' artifact contains accuracy scores for each coordinate, and 'prediction-regression' contains linear regression results for predicted vs. actual coordinates.

This is where q2-coordinates comes in. We can pass these results to the visualizer map-predicted-coordinates to visualize these results, mapping actual and predicted coordinates for each sample onto a map.
```
qiime coordinates map-predicted-coordinates --i-predictions coord-predictions.qza --i-prediction-regression coord-regression.qza --m-metadata-file chardonnay.map.txt --p-latitude latitude --p-longitude longitude --p-pred-lat latitude --p-pred-long longitude --o-visualization prediction-map
```
