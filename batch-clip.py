#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script that batch clips geofabrik osm shapfiles and projects them if needed.
"""
try:
  from osgeo import ogr, osr
  print 'Import of ogr from osgeo worked.  Proceed with clipping shapes with ogr2ogr!\n'
except:
  print 'Import of ogr from osgeo failed. Running backup methods.\n\n'

import subprocess, os, sys

#regexGK = re.compile('(gk)\d+')
#regexNegative = re.compile('(arc|style|datenblatt|AGB|Allgemeine|General)')
inputDir = "/Users/Valentin/Documents/github/clip-geofabrik/shapefiles"
outputDir = '' #Default setting, new files will be in same directory as input files + _clip.shp extension
clipPolygon = "/Users/Valentin/Documents/github/clip-geofabrik/clippingPolygon_31.shp"
targetSpatialReference = 'EPSG:31468' #Default: will use projection of clipping layer as target projection

# getting spatial reference of clipping polygon
driver = ogr.GetDriverByName('ESRI Shapefile')
if os.path.isfile(clipPolygon):
    dataset = driver.Open(os.path.abspath(clipPolygon))
    # get spatial reference from shapefile layer
    layer = dataset.GetLayer()
    spatialRefClippingPolygon = layer.GetSpatialRef()
    print spatialRefClippingPolygon
    if targetSpatialReference == '':
        targetSpatialReference = spatialRefClippingPolygon
        target_srs = os.path.join(os.path.abspath(inputDir),'target_srs.wkt')
        with open(target_srs, 'w') as file:
            file.write(targetSpatialReference.ExportToWkt())
else:
    print "The provided path to the clipping polygon does not point to a valid file! Exiting program..."
    sys.exit()



# walk directory and do gdal
for root, direc, files in os.walk(inputDir):
        for file1 in files:
            if file1[-4:] == '.shp' and ('_clip' not in file1):
                # 1. create new filename with _clip
                clipFile = file1[:-4]+'_clip.shp' # new shapefile name
                if outputDir == '':
                    clipPath = os.path.join(os.path.abspath(root),clipFile) # new path to clipping shapefile
                else:
                    clipPath = os.path.join(os.path.abspath(outputDir),clipFile) # new path to clipping shapefile

                clipOrigPath = os.path.join(os.path.abspath(root),file1) #path to original shapefile

                # 2. Compare projections and reproject clippingpolygon to original spatial reference
                # (a reprojection of all clipped data is done afterwards. That is much faster, as the original data is huge!)
                datasetOrig = driver.Open(os.path.abspath(clipOrigPath))
                # get spatial reference from shapefile layer
                layerOrig = datasetOrig.GetLayer()
                spatialRefOrig = layerOrig.GetSpatialRef()

                if not spatialRefOrig == spatialRefClippingPolygon: #if they dont match: reproject clipping polygon
                    orig_srs = os.path.join(os.path.abspath(inputDir),'orig_srs.wkt')
                    with open(orig_srs, 'w') as file:
                        file.write(spatialRefOrig.ExportToWkt())
                    # ogr2ogr -f "ESRI Shapefile" original.shp wgs84.shp -s_srs EPSG:27700 -t_srs EPSG:4326
                    command = ['ogr2ogr', '-f','ESRI Shapefile', '-overwrite',clipPolygon, clipPolygon[:-4]+'_reproj.shp', '-t_srs', orig_srs]
                    print "Subprocessing is running following line of code:\n"
                    print command
                    subprocess.check_call(command)
                    print "successfully reprojected clipping polygon"
                    #TODO update spatial reference and file path to reprojected layer file
                    clipPolygon = clipPolygon[:-4]+'_reproj.shp'
                    dataset = driver.Open(os.path.abspath(clipPolygon))
                    layer = dataset.GetLayer()
                    spatialRefClippingPolygon = layer.GetSpatialRef()

                # 3. call ogr2ogr to clip shapefiles
                # ogr2ogr -clipsrc clipping_polygon.shp output.shp input.shp
                if os.path.isfile(clipPath):
                    os.remove(clipPath)

                callArgs = ['ogr2ogr', '-clipsrc', clipPolygon, clipPath, clipOrigPath]
                print "Subprocessing is clipping shapefile with following arguments:\n"
                print callArgs
                subprocess.check_call(callArgs)

                #4. reproject all data back to spatial reference of clipping polygon
                if not spatialRefOrig == targetSpatialReference:
                    orig_srs = os.path.join(os.path.abspath(inputDir),'orig_srs.wkt')
                    with open(orig_srs, 'w') as file:
                        file.write(spatialRefOrig.ExportToWkt())

                    # ogr2ogr -f "ESRI Shapefile" original.shp wgs84.shp -s_srs EPSG:27700 -t_srs EPSG:4326
                    command = ['ogr2ogr', '-f','ESRI Shapefile', '-overwrite', clipPath, clipPath[:-4]+'_reproj.shp','-s_srs', orig_srs, '-t_srs', target_srs]
                    print "Subprocessing is running following line of code:\n"
                    print command
                    subprocess.check_call(command)
