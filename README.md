# nclidartools

NC Lidar Tools
Author: Corey Scheip, North Carolina State University. For questions, email cmscheip@ncsu.edu

Version: 2.1 /// Date: 2019-02-26

Description:
NC Lidar Tools is a Python-driven ArcGIS toolbox to aid in processing the new, public submeter NC QL2 Lidar Data
collected in 2014-2017. Data is available here: https://sdd.nc.gov/sdd/DataDownload.aspx The two main options for 
data download are QL2 Data (2 points/m2) or Elevation DEMs. The QL2 data is distributed as an LAS file of the 
selected area. The Elevation DEM is distributed as individual TIF tiles at a predetermined resolution. The QL2 data
allows the user to develop full resolution DEMs (0.5m spacing) or coarser as required. The Elevation TIF files are
set to the downloaded version (e.g. 1m spacing). This tool allows quick conversion of the full resolution, QL2
data into a user-specified resolution DEM and calculates hillshade and slope rasters on the dataset. 

This tool has not been fully tested on *non-NC* LAS files but there is no inherent reason this shouldn't work for 
these data as well. Try it out on a single or series of LAS files and let me know what you find!

Tools:
...las2dem
This tool takes an input LAS file or series of LAS files from the NC Spatial Data Download QL2 product page, creates
an las dataset, filters the dataset return values (if user selects filter value), creates an elevation raster at a
user-specified resolution (max of 0.5m for NC QL2 data), and if specified by user, creates a hillshade and slope
raster. All rasters are added to the map.


Software:
Tested on ArcGIS Desktop 10.6. Spatial Analyst required.

[end]
