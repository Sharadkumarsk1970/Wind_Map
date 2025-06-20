# Wind_Map
Visualizes 10-meter wind streamlines over India using ERA5 reanalysis data, generating a high-quality animated GIF clipped to India's boundary to show wind speed and direction over time.



Wind Streamline Visualization Over India
This project visualizes 10-meter wind streamlines over India using hourly ERA5 reanalysis data. It generates a high-quality animated GIF clipped to India's boundary, highlighting wind speed and direction over time — perfect for climate, meteorological, or geospatial data analysis.

Tech Stack & Libraries
Python – core language for data processing and visualization

xarray – for handling multi-dimensional ERA5 NetCDF data

geopandas & shapely – for spatial operations and masking to India’s boundary

matplotlib & cartopy – for rendering beautiful geospatial maps

imageio – to create smooth in-memory GIF animations

numpy & pandas – for numerical computations and time handling

Features
ERA5 hourly data visualized as streamlines

Spatial masking to Indian boundary using GeoJSON

Black-themed, annotated maps with lat/lon gridlines

In-memory GIF generation for speed and efficiency

Optimized frame sampling (every 6 hours) for faster rendering
