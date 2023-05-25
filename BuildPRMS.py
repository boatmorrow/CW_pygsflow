###############################################################################
# Build SURFACE GSFLOW MODEL - PRMS - inital model
# Cap Wallace Modeling project
# W. Payton Gardner
# University of Montana
# School of Forestry and Conservation
###############################################################################

#Build modflow model

#imports
import os
import utm
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import flopy
import platform
from gsflow.builder import GenerateFishnet, FlowAccumulation
import pdb
from gsflow.builder import PrmsBuilder

##################################################
# Input path management
##################################################

# set our cell size in meters.  #I'll start out with 100m for now, but will likely refine
cellsize=100
method = "nearest"

#model name
model_name = "Elkcreek_%3im"%cellsize+method

#toplevel ouput path
model_path = os.path.join("models",model_name)

#derived gis output path
gis_derived_path = os.path.join(model_path,"gis_deriv")

#gis data path
gis_data_path = os.path.join('data','gis')


#file names
dfname = "DEMResampled.txt"
flowdirname = "flowdir.txt"
flowaccname = "flowacc.txt"
watershedname = "watershed.txt"
gridname = "grid.bin"
streamfilename = "streams.bin"
cascadefilename = 'cascades.bin'
paramfilename = model_name+'_initial_prms.params'


## set the path to the mfnwt executable # in same directory as scripts.
#exe_name = os.path.join("/Users/wpgardner/soft/modflow/pymake/examples/mfnwt")


dem_file = os.path.join(gis_derived_path, dfname)
flowacc_file = os.path.join(gis_derived_path, flowaccname)
flowdir_file = os.path.join(gis_derived_path, flowdirname)
watershed_file = os.path.join(gis_derived_path, watershedname)
mg_file = os.path.join(model_path, gridname)

# define the stream information binary data path
stream_file = os.path.join(model_path, streamfilename)
cascade_file = os.path.join(model_path, cascadefilename)

#parameter file output
param_file = os.path.join(model_path,paramfilename)


#######################################################
#Load Data
#######################################################
# load modelgrid, dem, watershed, stream information, and cascade routing file
modelgrid = GenerateFishnet.load_from_file(mg_file)
dem_data = np.genfromtxt(dem_file)
watershed = np.genfromtxt(watershed_file, dtype=int)
strm_obj = FlowAccumulation.load_streams(stream_file)
cascades = FlowAccumulation.load_cascades(cascade_file)

#######################################################
#Build Initial PRMS model in one step
#######################################################
prmsbuild = PrmsBuilder(
    strm_obj,
    cascades,
    modelgrid,
    dem_data.ravel(),
    hru_type=watershed.ravel(),
    hru_subbasin=watershed.ravel()
)

################
# Build parameters
################
parameters = prmsbuild.build()


################
# Modify parameters - change to lat/long
################

lat, lon = utm.to_latlon(
    modelgrid.xcellcenters.ravel(),
    modelgrid.ycellcenters.ravel(),
    12,
    "N"
)

# set hru_lat and hru_lon values, using dynamic methods
parameters.hru_lat = lat
parameters.hru_lon = lon

#check conversion
if not np.allclose(parameters.hru_lat.values, lat):
    raise Exception()

if not np.allclose(parameters.hru_lon.values, lon):
    raise Exception()

print(parameters.hru_lon)    
print(type(parameters.hru_lon))

#######################################################
#Wrie Parmas file
#######################################################
parameters.write(param_file)