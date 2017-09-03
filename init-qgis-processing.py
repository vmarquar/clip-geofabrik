# -*- coding: utf-8 -*-

# 1. QGIS Mac Version
import os
import sys
sys.path.append('/Applications/QGis.app/Contents/Resources/python/')
sys.path.append('/Applications/QGis.app/Contents/Resources/python/plugins') # if you want to use the processing module, for example
from qgis.core import *
app = QgsApplication([],True)
QgsApplication.setPrefixPath("/Applications/QGIS.app/Contents/Plugins", True)
QgsApplication.initQgis()
import processing # all the steps above need to be done on  a mac version of qgis installed my kyngchaos
# initialize processing
from processing.core.Processing import Processing
Processing.initialize()
Processing.updateAlgsList()

# run algorithms
processing.alghelp("qgis:clip")
processing.runalg("qgis:clip",inputlayer,overlaylayer,"output_file.shp")
