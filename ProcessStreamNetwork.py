###############################################################################
# Hydrologic Processing for GSFLOW GRID - stream routing and cascades
# Cap Wallace Modeling project
# W. Payton Gardner
# University of Montana
# School of Forestry and Conservation
###############################################################################

#calulate stream networks and cascades

#imports
import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pdb
import flopy
from gsflow.builder import GenerateFishnet
from gsflow.builder import FlowAccumulation
import shapefile


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
shp_file_nm="ElkCreekPourPoint.shp"
dfname = "DEMResampled.txt"
flowdirname = "flowdir.txt"
flowaccname = "flowacc.txt"

## shapefile pour point
shp_file = os.path.join(gis_data_path,shp_file_nm)
dem_file = os.path.join(gis_derived_path, dfname)
flowacc_file = os.path.join(gis_derived_path, flowaccname)
flowdir_file = os.path.join(gis_derived_path, flowdirname)
mg_file = os.path.join(model_path, "grid.bin")

#file names
shp_file_nm="ElkCreekPourPoint.shp"
dfname = "DEMResampled.txt"
flowdirname = "flowdir.txt"
flowaccname = "flowacc.txt"
watershedname = "watershed.txt"
gridname = "grid.bin"

## shapefile pour point
shp_file = os.path.join(gis_data_path,shp_file_nm)
dem_file = os.path.join(gis_derived_path, dfname)
flowacc_file = os.path.join(gis_derived_path, flowaccname)
flowdir_file = os.path.join(gis_derived_path, flowdirname)
watershed_file = os.path.join(gis_derived_path, watershedname)
mg_file = os.path.join(model_path, gridname)

#######################################################
#Load Data
#######################################################
# load modelgrid, dem, flow directions, and flow accumulation
modelgrid = GenerateFishnet.load_from_file(mg_file)
dem_data = np.genfromtxt(dem_file)
flow_directions = np.genfromtxt(flowdir_file, dtype=float)
flow_accumulation = np.genfromtxt(flowacc_file)
watershed = np.genfromtxt(watershed_file, dtype=int)


##Flow Accumulation Class
fa = FlowAccumulation(
    dem_data,
    modelgrid.xcellcenters,
    modelgrid.ycellcenters,
    hru_type=watershed,
    flow_dir_array=flow_directions,
    verbose=True
)

#######################################################
#PROCESS STREAMS
#######################################################

#area threshold - this one seems to simplify the stream network to a reasonable amount
threshold_m2 = 3e6
threshold = threshold_m2 / (cellsize ** 2) #threshold is in cells, not area like Q

# run make streams
strm_obj = fa.make_streams(
    flow_directions,
    flow_accumulation,
    threshold,
 #   min_stream_len=10,  #don't want too many short reaches for now.   Could potentially be relaxed later.
    max_slope=1
)


#Visualize the Solution
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(1, 1, 1, aspect="equal")
pmv = flopy.plot.PlotMapView(modelgrid=modelgrid, ax=ax)
# plot the watershed boundary on top

pmv.plot_array(
    dem_data, vmin=dem_data.min(), vmax=dem_data.max(), cmap='Greys'
)
ib = pmv.plot_ibound(ibound=watershed)
pc = pmv.plot_array(strm_obj.iseg, masked_values=[0,])

plt.colorbar(pc, shrink=0.7)
plt.title("Elk Creek 100m stream segments")
plt.show()

#######################################################
#PROCESS CASCADES
#######################################################
#Cascades are the PRMS connectivity maps.  

#pour point
# read in our pour point from a shapefile as an xy coordinate
with shapefile.Reader(shp_file) as r:
    shape = r.shape(0)
    pour_point = shape.points

print(pour_point)

#cascade routing
cascades = fa.get_cascades(
    strm_obj,
    pour_point,
    modelgrid,
    fmt="xy"
)

# get ncascades
print("Number of cascades = %.3i" %(cascades.ncascade))


#######################################################
#Save Data
#######################################################

strm_obj.write(os.path.join(model_path, "streams.bin"))
cascades.write(os.path.join(model_path, "cascades.bin"))