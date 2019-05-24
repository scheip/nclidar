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
except:
    printArc('ABORTING SCRIPT. You need Spatial Analyst to run this tool')
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
returnClass1 = sys.argv[5]
returnClass2 = sys.argv[6]
if sys.argv[7] == '#' or sys.argv[7] == '':
    sr = arcpy.SpatialReference(26917)  # UTM 17N
else:
    srText = sys.argv[7]
    sr = arcpy.SpatialReference()  # an empty spatial reference object
    sr.loadFromString(srText) # get arcpy spatial reference object
targetElevUnits = sys.argv[8]
resolution = sys.argv[9]
hillshade = boolify(sys.argv[10])
az = float(sys.argv[11])
alt = float(sys.argv[12])
slope = boolify(sys.argv[13])
#aspect = boolify(sys.argv[14])

# Find las files in directory
idList = []
with arcpy.da.SearchCursor(tileScheme, 'Tile_Name') as sc:
    for row in sc:
        idList.append(row[0])

files = os.listdir(lasFileDir)
lasFiles = []
for fil in files:
    for id in idList:
        if fil.endswith('las') and id in fil:
            lasFiles.append(os.path.join(lasFileDir, fil))

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

# Determine surface constraint polygon
selecPolys = os.path.join(outDir, 'tiles.shp')
arcpy.Merge_management(tileScheme, selecPolys)
mergePolys = os.path.join(outDir, 'tiles_merge.shp')
arcpy.Merge_management(selecPolys, mergePolys)
surfConstr = '{0} <None> Hard_Clip'.format(mergePolys)

# Create *lasd
printArc('...creating LAS dataset...')
lasD = site + '.lasd'
# Create lasD for all returns
arcpy.CreateLasDataset_management(lasFiles, lasD, '#', surfConstr,
                                  '#', 'NO_COMPUTE_STATS', 'RELATIVE_PATHS')

# Filter *lasd for specified returns
printArc('...filtering LAS dataset...')
lasDFilter = site + '_filt.lasd'

if returnClass1 == 'All Returns':
    arcpy.MakeLasDatasetLayer_management(lasD, lasDFilter)
else:
    returnClassVal1 = int(returnClass1[0])
    try:
        returnClassVal2 = int(returnClass2[0])
        returnClassVals = [returnClassVal1, returnClassVal2]
    except:
        returnClassVals = returnClassVal1

    arcpy.MakeLasDatasetLayer_management(lasD, lasDFilter, returnClassVals)


# Create elevation DEM
printArc('...creating elevation DEM...')
start = datetime.datetime.now()
elevDEM = 'el' + site
interp = "BINNING AVERAGE NATURAL_NEIGHBOR"
arcpy.LasDatasetToRaster_conversion(lasDFilter, elevDEM, 'ELEVATION',\
                                    interp, 'FLOAT', 'CELLSIZE', resolution, 1)

# Adjust Z-units

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

# File management
arcpy.Delete_management(selecPolys)

printArc('--- Finished ' + site.upper() + ' ---')
printArc('')

del mxd
