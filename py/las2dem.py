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
if sys.argv[3] == '#' or sys.argv[4] == '':
    site = os.path.basename(outDir)[0:8]
else:
    site = sys.argv[3][0:8]
returnClass1 = sys.argv[4]
returnClass2 = sys.argv[5]
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
curv = boolify(sys.argv[13])

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

printArc('--- Beginning ' + site.upper() + ' ---')

# Create *lasd
printArc('...creating LAS dataset...')
lasD = site + '.lasd'
arcpy.CreateLasDataset_management(lasFiles, lasD, '#', '#',
                                  '#', '#', 'RELATIVE_PATHS', 'FILES_MISSING_PROJECTION')

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
elevDEM = 'el_' + site
interp = "BINNING AVERAGE NATURAL_NEIGHBOR"
arcpy.LasDatasetToRaster_conversion(lasDFilter, elevDEM, 'ELEVATION',\
                                    interp, 'FLOAT', 'CELLSIZE', resolution, 1)
arcpy.BuildPyramids_management(in_raster_dataset=elevDEM)

elevDEMlyr = arcpy.mapping.Layer(elevDEM)
checkAddLyr(elevDEMlyr)
printArc('elapsed time for DEM: %s\n\n' % (datetime.datetime.now() - start))

# Create hillshade
if hillshade:
    printArc('...creating hillshade raster...')
    start = datetime.datetime.now()

    hillRas = 'hs_' + site
    hillRasObject = arcpy.sa.Hillshade(elevDEM, az, alt, 'NO_SHADOWS', 1)
    hillRasObject.save(hillRas)
    del hillRasObject

    arcpy.BuildPyramids_management(in_raster_dataset=hillRas)

    hillLyr = arcpy.mapping.Layer(hillRas)
    checkAddLyr(hillLyr)
    printArc('elapsed time for Hillshade: %s\n\n' % (datetime.datetime.now() - start))

# Create slope
if slope:
    printArc('...creating slope raster...')
    start = datetime.datetime.now()
    slopeRas = 'slp_' + site
    slopeRasObject = arcpy.sa.Slope(elevDEM, "DEGREE", 1)
    slopeRasObject.save(slopeRas)
    del slopeRasObject

    arcpy.BuildPyramids_management(in_raster_dataset=slopeRas)

    slopeLyr = arcpy.mapping.Layer(slopeRas)
    checkAddLyr(slopeLyr)
    printArc('elapsed time for Slope: %s\n\n' % (datetime.datetime.now() - start))


# Create curvature rasters
if curv:
    printArc('...creating curvature rasters...')
    start = datetime.datetime.now()
    curveDir = os.path.join(outDir, 'curvature')
    checkAddDir(curveDir)
    arcpy.env.workspace = curveDir
    curveRas = 'cv_' + site
    profCurveRas = 'pfcv_' + site
    planCurveRas = 'pncv_' + site


    curveRasObject = arcpy.sa.Curvature(elevDEM, 1, profCurveRas, planCurveRas)
    curveRasObject.save(curveRas)
    del curveRasObject

    arcpy.BuildPyramids_management(in_raster_dataset=curveRas)
    arcpy.BuildPyramids_management(in_raster_dataset=profCurveRas)
    arcpy.BuildPyramids_management(in_raster_dataset=planCurveRas)

    curveLyr = arcpy.mapping.Layer(curveRas)
    checkAddLyr(curveLyr)
    profCurveLyr = arcpy.mapping.Layer(profCurveRas)
    checkAddLyr(profCurveLyr)
    planCurveLyr = arcpy.mapping.Layer(planCurveRas)
    checkAddLyr(planCurveLyr)
    printArc('elapsed time for Curvature: %s\n\n' % (datetime.datetime.now() - start))



printArc('--- Finished ' + site.upper() + ' ---')
printArc('')

del mxd

