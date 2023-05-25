###############################################################################
# Build GSFLOW MODEL - GSFLOW - inital model
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
from gsflow.builder import ControlFileBuilder
import gsflow

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
mfname = model_name+'.nam'
paramfilename = model_name+'_initial_prms.params'
controlfilename = model_name+'_initial_gflow.control'

## set the path to the mfnwt executable # in same directory as scripts.

#modflow file
mf_file = os.path.join(model_path,mfname)
#parameter file 
param_file = os.path.join(model_path,paramfilename)
#control file
control_file = os.path.join(model_path,controlfilename)

#######################################################
#Load Data
#######################################################
#load modflow model
ml = gsflow.modflow.Modflow.load(mfname, model_ws=model_path)
parameters = gsflow.prms.PrmsParameters.load_from_file(param_file)

#######################################################
#Build Control Object
#######################################################

#Using TONS of defaults here.  
controlbuild = ControlFileBuilder()

control = controlbuild.build(model_name, parameters, ml)
print(type(control))

###################
# Update a Control Parameter 
###################
control.model_mode = ["GSFLOW5",]

print(control.model_mode)

#######################################################
#Write Control File
#######################################################
control.write(control_file)
