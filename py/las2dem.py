#------------------------------
# script name: las2dem.py
# project name: py
#
#
# Author: Corey Scheip, cmscheip@ncsu.edu
#
# Creation date: 12/30/2018
#
#------------------------------

import arcpy
import sys
import datetime
import os

""" debug
lasFilesIn = "G:\lidar_data\QL2\stone\\22030_1.las"
lasFiles = lasFilesIn.split(';')
returnClass = "2 —Bare earth measurements"
sr = ''
targetElevUnits = 'meter'
resolution = 0.5
hillshade = True
az = float('315')
alt = float('45')
slope = True
aspect = False
"""

def printArc(message):
    '''Print message for script tool and standard output.'''
    print message
    arcpy.AddMessage(message)


def checkAddLyr(layer):
    if arcpy.mapping.ListLayers(mxd, layer, df):
        arcpy.mapping.RemoveLayer(df, layer)
    arcpy.mapping.AddLayer(df, layer)


def checkAddDir(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)
        printArc('Output folder created: {0}'.format(directory))

def boolify(param):
    if param == 'true':
        param = True
    elif param == 'false':
        param = False

    return param


# Check for spatial analyst, if not available, abort!
try:
    arcpy.CheckOutExtension('Spatial')
    arcpy.CheckOutExtension('3D')
except:
    printArc('ABORTING SCRIPT. You need 3D Analyst and Spatial Analyst to run this tool')
    sys.exit(0)

# Set environment vars
arcpy.env.overwriteOutput = True

# Set user variables
lasFilesIn = sys.argv[1]
lasFiles = lasFilesIn.split(';')
if sys.argv[2] == '#' or sys.argv[2] == '':
    outDir = os.path.dirname(lasFiles[0])
else:
    outDir = sys.argv[2]
returnClass = sys.argv[3]
if sys.argv[4] == '#' or sys.argv[4] == '':
    sr = arcpy.SpatialReference(26917)  # UTM 17N
else:
    srText = sys.argv[4]
    sr = arcpy.SpatialReference()  # an empty spatial reference object
    sr.loadFromString(srText) # get arcpy spatial reference object

targetElevUnits = sys.argv[5]
resolution = sys.argv[6]
hillshade = boolify(sys.argv[7])
az = float(sys.argv[8])
alt = float(sys.argv[9])
slope = boolify(sys.argv[10])
#aspect = boolify(sys.argv[11])

# Check for space in output directory
if ' ' in outDir:
    printArc('ERROR --- Remove space from output directory --- ERROR')
    sys.exit(0)

arcpy.env.outputCoordinateSystem = sr
linUnit = str(sr.linearUnitName)

# Set up Map Doc
mxd = arcpy.mapping.MapDocument('CURRENT')
df = arcpy.mapping.ListDataFrames(mxd)[0]

# Set up workspace
arcpy.env.workspace = outDir
site = os.path.basename(outDir)[0:11]

printArc('--- Beginning ' + site.upper() + ' ---')

# Create *lasd
printArc('...creating LAS dataset...')
lasD = site + '.lasd'
arcpy.CreateLasDataset_management(lasFiles, lasD, '#', '#',
                                  '#', '#', 'RELATIVE_PATHS', 'FILES_MISSING_PROJECTION')

# Filter *lasd for specified returns
printArc('...filtering LAS dataset...')
lasDFilter = site + '_filt.lasd'

if returnClass == 'All Returns':
    arcpy.MakeLasDatasetLayer_management(lasD, lasDFilter)
elif returnClass == 'First Return (DSM)':
    #arcpy.MakeLasDatasetLayer_management(lasD, lasDFilter, '#', 'First of Many')
    arcpy.MakeLasDatasetLayer_management(lasD, lasDFilter, '#', '1')
else:
    returnClassVal = int(returnClass[0])
    arcpy.MakeLasDatasetLayer_management(lasD, lasDFilter, returnClassVal)


# Create elevation DEM
printArc('...creating elevation DEM...')
start = datetime.datetime.now()
elevDEM = 'el' + site
interp = "BINNING AVERAGE NATURAL_NEIGHBOR"
arcpy.LasDatasetToRaster_conversion(lasDFilter, elevDEM, 'ELEVATION',\
                                    interp, 'FLOAT', 'CELLSIZE', resolution, 1)

elevDEMlyr = arcpy.mapping.Layer(elevDEM)
checkAddLyr(elevDEMlyr)
printArc('elapsed time for DEM: %s\n\n' % (datetime.datetime.now() - start))

# Create hillshade
if hillshade:
    printArc('...creating hillshade raster...')
    start = datetime.datetime.now()

    hillRas = 'hi' + site
    hillRasObject = arcpy.sa.Hillshade(elevDEM, az, alt, 'NO_SHADOWS', 1)
    hillRasObject.save(hillRas)
    del hillRasObject

    hillLyr = arcpy.mapping.Layer(hillRas)
    checkAddLyr(hillLyr)
    printArc('elapsed time for Hillshade: %s\n\n' % (datetime.datetime.now() - start))

# Create slope
if slope:
    printArc('...creating slope raster...')
    start = datetime.datetime.now()
    slopeRas = 'sl' + site
    slopeRasObject = arcpy.sa.Slope(elevDEM, "DEGREE", 1)
    slopeRasObject.save(slopeRas)
    del slopeRasObject

    slopeLyr = arcpy.mapping.Layer(slopeRas)
    checkAddLyr(slopeLyr)
    printArc('elapsed time for Slope: %s\n\n' % (datetime.datetime.now() - start))


printArc('--- Finished ' + site.upper() + ' ---')
printArc('')

del mxd
