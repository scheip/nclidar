# nclidartools

NC Lidar Tools /// Author: Corey Scheip, North Carolina State University. For questions, email cmscheip@ncsu.edu

Version: 2.2 /// Date: 2019-05-31

Description:
NC Lidar Tools is a Python-driven ArcGIS toolbox to aid in processing the new, public submeter NC QL1/QL2 Lidar Data
collected in 2014-2017. Data is available here: https://sdd.nc.gov/sdd/DataDownload.aspx The two main options for 
data download are QL1/QL2 Data (>2 points/m2) or preprocessed Elevation DEMs (min resolution 1m). The QL1/QL2 data is
distributed as an LAS file of the selected are or you can obtain a larger dataset (e.g. county) with supporting files like the Tile Scheme, via a large data request to the NC Dept. of Public Safety. This tool allows quick conversion of the full resolution, QL1/QL2 data into a user-specified resolution DEM and calculates hillshade and slope rasters on the dataset. 

This tool has not been fully tested on *non-NC* LAS files but there is no inherent reason this shouldn't work for 
these data as well. Try it out on a single or series of LAS files and let me know what you find!

*Updates to v2.2 (2019-05-31):
Added tool LAS Picker. LAS Picker allows the user to select tiles from the Tile Scheme that ships with a full suite of LAS data from NC Department of Public Safety data transfer. LAS Picker identifies the selected tiles and processes those into a single DEM and other specified raster derivatives (e.g., hillshade, slope). As of release of this tool, there is no sample data associated with it. Email cmscheip@ncsu.edu for assistance.*

*Updates to v2.1 (2019-02-26):
Fixed two known bugs - 1) space in output directory error and 2) character length limit. Script now exits if space is in output directory and truncates site name to fit within ArcGIS character limits. 
Added Output directory capability. By default, tool will place files in folder of LAS data, but allows user to specify alternate output location.*

Tools:
...las2dem
This tool takes an input LAS file or series of LAS files from the NC Spatial Data Download QL2 product page, creates
an las dataset, filters the dataset return values (if user selects filter value), creates an elevation raster at a
user-specified resolution (max of 0.5m for NC QL2 data), and if specified by user, creates a hillshade and slope
raster. All rasters are added to the map.

...lasPicker
To use this tool, load the tile scheme into a map document. Select the tiles you'd like to process. Open the tool dialog, and select the tile scheme from the drop down menu. This will tell the tool to only pull the selected tiles. It is recommended to select an output directory, otherwise the resulting rasters will be deployed into the LAS file directory and this could get messy depending on your file structure. This script has been tested on as few as 1 tile up to 1,500+ tiles. To process an entire county in the mountains of NC to full 0.5-meter resolution, expect a 12+ hour run time. Rasters are added to the map document.


Software:
Tested on ArcGIS Desktop 10.6. Spatial Analyst required.

[end]
