#------------------------------
# script name: lasLooper.py
# project name: py
#
#
# Author: Corey Scheip, cmscheip@ncsu.edu
#
# Creation date: 4/27/2018
#
#------------------------------

import arcpy
import sys
import datetime
import os

""" debug
tileScheme = 
lasFileDir = 
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
tileScheme = sys.argv[1]
lasFileDir = sys.argv[2]
if sys.argv[3] == '#' or sys.argv[3] == '':
    outDir = lasFileDir
else:
    outDir = sys.argv[3]
if sys.argv[4] == '#' or sys.argv[4] == '':
    site = os.path.basename(outDir)[0:11]
else:
    site = sys.argv[4][0:11]
returnClass = sys.argv[5]
if sys.argv[6] == '#' or sys.argv[6] == '':
    sr = arcpy.SpatialReference(26917)  # UTM 17N
else:
    srText = sys.argv[6]
    sr = arcpy.SpatialReference()  # an empty spatial reference object
    sr.loadFromString(srText) # get arcpy spatial reference object
targetElevUnits = sys.argv[7]
resolution = sys.argv[8]
hillshade = boolify(sys.argv[9])
az = float(sys.argv[10])
alt = float(sys.argv[11])
slope = boolify(sys.argv[12])
#aspect = boolify(sys.argv[13])

# Find las files in directory
idList = []
with arcpy.da.SearchCursor(tileScheme, 'LiDARTiles') as sc:
    for row in sc:
        idList.append(row[0])

files = os.listdir(lasFileDir)
lasFiles=[]
for fil in files:
    for id in idList:
        if fil.endswith('las') and id in fil:
            lasFiles.append(os.path.join(lasFileDir ,fil))

# Check for space in output directory
if ' ' in outDir:
    printArc('ERROR --- Remove space (' ') from output directory --- ERROR')
    sys.exit(0)

arcpy.env.outputCoordinateSystem = sr
linUnit = str(sr.linearUnitName)

# Set up Map Doc
mxd = arcpy.mapping.MapDocument('CURRENT')
df = arcpy.mapping.ListDataFrames(mxd)[0]

# Set up workspace
arcpy.env.workspace = outDir

printArc('--- Beginning ' + site.upper() + ' ---')

# Create *lasd
printArc('...creating LAS dataset...')
lasD = site + '.lasd'
# The below filters for ground. Should add to the gui for user selection
arcpy.CreateLasDataset_management(lasFiles, lasD, '#', '#',
                                  '#', '#', 'RELATIVE_PATHS', 'FILES_MISSING_PROJECTION')

# Filter *lasd for specified returns
printArc('...filtering LAS dataset...')
lasDFilter = site + '_filt.lasd'

if returnClass == 'All Returns':
    arcpy.MakeLasDatasetLayer_management(lasD, lasDFilter)
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
