#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Written in python 2.7
Script that batch clips geofabrik osm shapfiles and projects them if needed. Optimized for arcpy / ArcGIS Use
Example output:
python batch-clip -h
python batch-clip.py -in=shapefiles -m=polygon.shp -t_srs=EPSG:1234 -s_srs=EPSG:4236 [-out=output/directory]
python batch-clip.py --inputDir=/Users/Valentin/Documents/github/clip-geofabrik/shapefiles --mask=/Users/Valentin/Documents/github/clip-geofabrik/shapefiles/clippingPoly.shp --target_srs=EPSG:31468 --source_srs=EPSG:4326
"""

import os, sys, argparse, arcpy

__author__ = 'Valentin Marquart'


def get_args():
    '''This function parses and return arguments passed in'''
    # Assign description to the help doc
    parser = argparse.ArgumentParser(
        description='Script clips shapefiles in a given folder and reprojects them')
    # Add arguments
    parser.add_argument(
        '-in', '--inputDir', type=str, help='Input directory without a trailing slash', required=True)
    parser.add_argument(
        '-m', '--mask', type=str, help='Absolute path to clipping feature', required=True)
    parser.add_argument(
        '-t_srs', '--target_srs', type=str, help='The spatial reference, where the clipped data should be projected into', required=True)
    parser.add_argument(
        '-s_srs', '--source_srs', type=str, help='The spatial reference, where the clipped data is in', required=True)
    parser.add_argument(
        '-out', '--outputDir', type=str, help='Output director, Default is the same as inout directory', required=False, default='')
    # Array for all arguments passed to script
    args = parser.parse_args()
    # Assign args to variables
    inputDir = args.inputDir
    clipPolygon = args.mask
    target_srs = args.target_srs
    orig_srs = args.source_srs
    outputDir = args.outputDir
    # Return all variable values
    return inputDir, clipPolygon, target_srs, orig_srs, outputDir

# Run get_args()
# get_args()

# Match return values from get_arguments()
# and assign to their respective variables
inputDir, clipPolygon, target_srs, orig_srs, outputDir = get_args()

# inputDir = "/Users/Valentin/Documents/github/clip-geofabrik/shapefiles"
# outputDir = '' #Default setting, new files will be in same directory as input files + _clip.shp extension
# clipPolygon = "/Users/Valentin/Documents/github/clip-geofabrik/shapefiles/clippingPoly.shp"
# target_srs = 'EPSG:31468' #Default: will use projection of clipping layer as target projection
# orig_srs = 'EPSG:4326' #WGS 84
ext = ['.shp','.shx','.dbf','.prj']


# getting spatial reference of clipping polygon
if os.path.isfile(clipPolygon):
    # get spatial reference from shapefile layer
    spatialRefClippingPolygon = arcpy.Describe(clipPolygon).spatialReference
    targetSpatialReference = spatialRefClippingPolygon
else:
    print "The provided path to the clipping polygon does not point to a valid file! Exiting program..."
    sys.exit()



# walk directory and do gdal
for root, direc, files in os.walk(inputDir):
        for file1 in files:
            if (file1[-4:] == '.shp') and ('_clip' not in file1) and (os.path.join(os.path.abspath(root),file1) != clipPolygon) and ('_reproj' not in file1):
                # 1. create new filename with _clip
                clipFile = file1[:-4]+'_clip.shp' # new shapefile name
                if outputDir == '':
                    clipPath = os.path.join(os.path.abspath(root),clipFile) # new path to clipping shapefile
                    outputDir = inputDir
                else:
                    clipPath = os.path.join(os.path.abspath(outputDir),clipFile) # new path to clipping shapefile

                clipOrigPath = os.path.join(os.path.abspath(root),file1) #path to original shapefile

                # 2. Compare projections and reproject clippingpolygon to original spatial reference
                # (a reprojection of all clipped data is done afterwards. That is much faster, as the original data is huge!)
                spatialRefOrig = arcpy.Describe(clipOrigPath).spatialReference

                if not spatialRefOrig == spatialRefClippingPolygon: #if they dont match: reproject clipping polygon
                    # ogr2ogr -f "ESRI Shapefile" original.shp wgs84.shp -s_srs EPSG:27700 -t_srs EPSG:4326
                    original_srs = arcpy.SpatialReference(int(orig_srs.split(':')[1]))
                    arcpy.env.overwriteOutput = True
                    arcpy.Project_management(clipPolygon, clipPolygon[:-4]+'_reproj.shp', original_srs)

                    print "Successfully reprojected clipping polygon!\n"
                    #TODO update spatial reference and file path to reprojected layer file
                    clipPolygon = clipPolygon[:-4]+'_reproj.shp'
                    spatialRefClippingPolygon = arcpy.Describe(clipPolygon).spatialReference

                # 3. call ogr2ogr to clip shapefiles
                # ogr2ogr -clipsrc clipping_polygon.shp output.shp input.shp
                if os.path.isfile(clipPath):
                    os.remove(clipPath)

                # Execute Clip
                arcpy.Clip_analysis(clipOrigPath, clipPolygon, clipPath, "")
                print "Successfully clipped {} polygon!\n".format(file1)


                # 4. reproject all data back to spatial reference of clipping polygon
                if not spatialRefOrig == targetSpatialReference:
                    target_srs = arcpy.SpatialReference(int(target_srs.split(':')[1]))
                    arcpy.env.overwriteOutput = True
                    arcpy.Project_management(clipPath, clipPath[:-4]+'_reproj.shp', target_srs)
                    print "Successfully reprojected {0} to {1}\n".format(clipPath,target_srs)

# removing files
print "Removing temporary files\n\n"
for root, direc, files in os.walk(outputDir):
        for file1 in files:
            if (file1[-9:-4] == '_clip') and (file1[-4:] in ext) or ('_reproj_reproj' in file1):
                #print "Removing {}".format(file1)
                os.remove(os.path.join(os.path.abspath(root),file1))
