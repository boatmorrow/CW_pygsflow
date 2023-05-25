###############################################################################
# Create Fishnet for GSFLOW GRID
# Cap Wallace Modeling project
# W. Payton Gardner
# University of Montana
# School of Forestry and Conservation
###############################################################################

# In this sript, we create a fishnet with the extents of a dem
# and lay it over the dem to visualize the spacing.
# We then save the fishnet as a grid for later use, and finally resample the dem
# to the grid.

# script is based off of pysflow tutorial 01 and 02 - the main inputs are:
    # dem file
    # grid size

import os
import matplotlib.pyplot as plt
import numpy as np
import flopy
from gsflow.builder import GenerateFishnet
import pdb
try:
    from numba import jit
    multithread = False
except ImportError:
    multithread = True
    print('No Numba')



##################################################
# Input path management
##################################################

# raster file - is a clipped section ned tile which contains the drainage - projected to utm zone 12N from QGIS
raster = os.path.join('data', 'gis', 'clipped_dem_ElkCreek.tif')
# set our cell size in meters.  #I'll start out with 100m for now, but will likely refine
cellsize=100
method = "nearest"

#model name
model_name = "Elkcreek_%3im"%cellsize+method

#toplevel ouput path
model_path = os.path.join("models",model_name)

#derived output path
gis_derived_path = os.path.join(model_path,"gis_deriv")

#grid file
fname="grid.bin"
grid_file = os.path.join(model_path, fname)
modelgrid = GenerateFishnet(raster, xcellsize=cellsize, ycellsize=cellsize)

# let's load the raster for plotting
robj = flopy.utils.Raster.load(raster)

# plot the fishnet on top of the raster imagery
fig, ax = plt.subplots(figsize=(10,9))
robj.plot(ax=ax)
modelgrid.plot(ax=ax,alpha=0.2)
ax.set_title("Fishnet generated from raster")

try:
    os.makedirs(gis_derived_path)
except FileExistsError:
    print('Model Directory Exists - Old files will be deleted and/or rewritten')
    
#Save File for later
modelgrid.write(grid_file)

###################################################
# Resample DEM to FISHNET for GSFLOW 
###################################################

# Resample the dem to the grid spacing.  
print(type(modelgrid))
print(modelgrid.__class__.__bases__)
print(modelgrid.extent)



# use multithreading with "median" method if Numba is not installed to improve speed. 
# This however still takes time and is the bottleneck in the model building process
dem_data = robj.resample_to_grid(
    modelgrid, 
    robj.bands[0], 
    method=method, 
    multithread=False, 
    thread_pool=12
)

# plot the resampled DEM with the modelgrid overlain
fig2 = plt.figure(figsize=(10,9))
ax2 = fig2.add_subplot(1, 1, 1, aspect="equal")

pmv = flopy.plot.PlotMapView(modelgrid=modelgrid, ax=ax2)
ax2 = pmv.plot_array(
    dem_data, masked_values=robj.nodatavals, vmin=dem_data.min(), vmax=dem_data.max()
)
lc = pmv.plot_grid(color="grey", lw=0.3)
plt.title("Elk Creek resampled DEM array")
plt.colorbar(ax2, shrink=0.7)
plt.tight_layout()
plt.show()

dfname = "DEMResampled.txt"
dfrname = "DEMResampled.tif"
dem_file = os.path.join(gis_derived_path,dfname)
raster_file = os.path.join(gis_derived_path,dfrname)

#######################################################
#Save Data
#######################################################

np.savetxt(dem_file, dem_data, delimiter="  ")

#output a tif file for post processing with SAGA.  
flopy.export.utils.export_array(modelgrid,raster_file,dem_data,fieldname='Elevation')