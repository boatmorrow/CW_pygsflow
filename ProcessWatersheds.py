###############################################################################
# Hydrologic Processing for GSFLOW GRID - watershed delineation
# Cap Wallace Modeling project
# W. Payton Gardner
# University of Montana
# School of Forestry and Conservation
###############################################################################

#calculate watershed delineations

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
dfname = "DEMResampledFA.txt"
flowdirname = "flowdir.txt"
flowaccname = "flowacc.txt"

## shapefile pour point
shp_file = os.path.join(gis_data_path,shp_file_nm)
dem_file = os.path.join(gis_derived_path, dfname)
flowacc_file = os.path.join(gis_derived_path, flowaccname)
flowdir_file = os.path.join(gis_derived_path, flowdirname)
mg_file = os.path.join(model_path, "grid.bin")

##############################################
#Load Data
##############################################

# define the modelgrid and resampled DEM data paths

# load modelgrid, dem, flow directions, and flow accumulation
modelgrid = GenerateFishnet.load_from_file(mg_file)
dem_data = np.genfromtxt(dem_file)
flow_directions = np.genfromtxt(flowdir_file)
flow_accumulation = np.genfromtxt(flowacc_file)

#fa object
fa = FlowAccumulation(
    dem_data,
    modelgrid.xcellcenters,
    modelgrid.ycellcenters,
    flow_dir_array=flow_directions,
    verbose=True
)


##############################################
#Get Watershed Area
##############################################
# read in our pour point from a shapefile as an xy coordinate
with shapefile.Reader(shp_file) as r:
    shape = r.shape(0)
    pour_point = shape.points

print(pour_point)

#pour_point=[[318167.0,5196244.8]]

xx = np.argmin(np.abs(modelgrid.xcellcenters[0,:]-pour_point[0][0]))
yy = np.argmin(np.abs(modelgrid.ycellcenters[:,0]-pour_point[0][1]))


#ELK CREEK WATERSHED
watershed = fa.define_watershed(pour_point, modelgrid, fmt="xy")

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(1, 1, 1, aspect="equal")

pmv = flopy.plot.PlotMapView(modelgrid=modelgrid, ax=ax)
pc = pmv.plot_array(
    watershed, vmin=0, vmax=1,
)
plt.plot(*pour_point[0], 'bo')
plt.colorbar(pc, shrink=0.7)
plt.title("Elk Creek 100m watershed delineation (yellow=active)")
plt.show()


#######################################################
#Subsheds
#######################################################
subshdfile="Subsheds.shp"
ss_shp_file = os.path.join(gis_data_path,subshdfile)
subbasins = fa.define_subbasins(
    ss_shp_file,
    modelgrid,
    fmt="shp"
)

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(1, 1, 1, aspect="equal")

pmv = flopy.plot.PlotMapView(modelgrid=modelgrid, ax=ax)
pmv.plot_array(
    dem_data, cmap='Greys'
)
pc = pmv.plot_array(
    subbasins, masked_values=[0,],alpha=0.4
)
#subshed points
r2 = shapefile.Reader(ss_shp_file)
for ss in r2.iterShapes():
    #pdb.set_trace()
    si = ss.points
    plt.plot(*si[0],'bo')

#######################################################
#Save Data
#######################################################

#for r, c in pour_points:
#    xc, yc = modelgrid.xcellcenters[r, c], modelgrid.ycellcenters[r, c]
#    plt.plot(xc, yc, 'ko', ms=4)
plt.colorbar(pc, shrink=0.7)
plt.title("Elk Creek 100m subbasin delineation")
plt.show()

np.savetxt(
    os.path.join(gis_derived_path, "watershed.txt"),
    watershed.astype(int),
    delimiter="  ",
    fmt="%d"
)

np.savetxt(
    os.path.join(gis_derived_path, "subbasin.txt"),
    subbasins.astype(int),
    delimiter="  ",
    fmt="%d"
)
