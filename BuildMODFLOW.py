###############################################################################
# Build SUBSURFACE GSFLOW MODEL - MODFLOW (NWT,SFR,UZF)
# Cap Wallace Modeling project
# W. Payton Gardner
# University of Montana
# School of Forestry and Conservation
###############################################################################

#Build modflow model

#imports
import os
import shapefile
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import flopy
import platform
from gsflow.builder import GenerateFishnet, FlowAccumulation
from gsflow.builder import ModflowBuilder
import pdb

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

#mf output path
#mf_path = os.path.join(model_path,'modflow')
mf_path = model_path

#file names
shp_file_nm="ElkCreekPourPoint.shp"
dfname = "DEMResampled.txt"
flowdirname = "flowdir.txt"
flowaccname = "flowacc.txt"
watershedname = "watershed.txt"
gridname = "grid.bin"
streamfilename = "streams.bin"

## set the path to the mfnwt executable # in same directory as scripts.
exe_name = os.path.join("/Users/wpgardner/soft/modflow/pymake/examples/mfnwt")

## shapefile pour point
shp_file = os.path.join(gis_data_path,shp_file_nm)
dem_file = os.path.join(gis_derived_path, dfname)
flowacc_file = os.path.join(gis_derived_path, flowaccname)
flowdir_file = os.path.join(gis_derived_path, flowdirname)
watershed_file = os.path.join(gis_derived_path, watershedname)
mg_file = os.path.join(model_path, gridname)

# define the stream information binary data path
stream_file = os.path.join(model_path, streamfilename)

#######################################################
#Load Data
#######################################################
# load modelgrid, dem, watershed, and stream information file
modelgrid = GenerateFishnet.load_from_file(mg_file)
dem_data = np.genfromtxt(dem_file)
watershed = np.genfromtxt(watershed_file, dtype=int)
strm_obj = FlowAccumulation.load_streams(stream_file)

#######################################################
#Build Initial MODFLOW model in one step
#######################################################
# create a new modflow builder object
#model_name="ElkCreek_100m"
mfbuild = ModflowBuilder(modelgrid, dem_data, model_name)

########
#1 Layer for now
########
# set the botm elevation to be 100 m less than the top
botm = dem_data - 100
#pdb.set_trace()
botm.shape = (1, modelgrid.nrow, modelgrid.ncol)

# build the model
ml = mfbuild.build_all(
    strm_obj.reach_data,
    strm_obj.segment_data,
    strm_obj.irunbnd,
    finf=np.ones(dem_data.shape),
    botm=botm,
    ibound=watershed,
    iuzfbnd=watershed
)

print(ml)


#######################################################
#Update MODFLOW Packages
#######################################################

#many of these just examples for now

##########################
# Update DIS
##########################

#dummy example of updating time disc.  just taken from tutorial for now
# create data for perlen, nstp, tsmult, and the steady flag
# Keeping things one layer for the time being.
perlen = [1,1]
nstp = [1,200]
tsmult = [1,1]
steady = [True,False]

dis = flopy.modflow.ModflowDis(
    ml,
    nlay=ml.dis.nlay,
    nrow=ml.dis.nrow,
    ncol=ml.dis.ncol,
    nper=2,
    delr=ml.dis.delr,
    delc=ml.dis.delc,
    laycbd=ml.dis.laycbd,
    top=ml.dis.top,
    botm=ml.dis.botm,
    perlen=perlen,
    nstp=nstp,
    tsmult=tsmult,
    steady=steady,
    itmuni=ml.dis.itmuni,
    lenuni=ml.dis.lenuni
)

print(ml)

##########################
# Update UPW
##########################

#going to keep these values from tutorial for now, but likely need to be tuned for the model later.

# update hk using a multiplier, current value is 10 m/d
ml.upw.hk *= 1.75e-03

# show how to update the ss using a multiplier, current value is 1e-06 and appropriate for this model
ml.upw.ss *= 1.0

##########################
# Update SFR
##########################

#going to keep these values from tutorial for now, but likely need to be tuned for the model later.

# update roughch in segment data
ml.sfr.segment_data[0]["roughch"] = 0.04

# update strhc1 in reach data
ml.sfr.reach_data["strhc1"] = 0.1

##########################
# Offset the Model GRID to match location
##########################
# copy the coordinate information from the modelgrid we built in the Fishnet
ml.modelgrid.set_coord_info(
    xoff=modelgrid.xoffset, 
    yoff=modelgrid.yoffset
)

##########################
# Write Input Files
##########################
# change the path of the model and write to file
ml.change_model_ws(mf_path)
ml.write_input()

#######################################################
#RUN MODFLOW 
#######################################################
ml.exe_name = exe_name
#pdb.set_trace()
success, buff = ml.run_model(silent=False)
print(success)

#######################################################
#Visualize the solution
#######################################################
# define the headfile path
head_file = os.path.join(mf_path, model_name+".hds")

# load the headfile
hds = flopy.utils.HeadFile(head_file)

# get data
heads = hds.get_alldata()[-1]

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(1, 1, 1, aspect="equal")

pmv = flopy.plot.PlotMapView(model=ml, ax=ax)
pc = pmv.plot_array(heads)
ib = pmv.plot_inactive()
plt.colorbar(pc, shrink=0.7)
plt.title("Elk Creek 100m modflow-nwt heads")
plt.tight_layout()
plt.show()

#final adjustments
# adjust SFR flow parameter to zero
ml.sfr.segment_data[0]["flow"] *= 0 

# write the model to file
ml.write_input()

