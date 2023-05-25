## GSFLOW Modeling Notes

#### 0) Hydrologic Processing of DEM
*  Ran into issues with the interpolated DEM, so I tried processing the high res dem first.
*  Think this first processing not worth it. See 2) below.

#### 1) ProcessesFishNet.py Resampling Hydro Proc DEM using GSFLOW builder
*   Just use nearest neighbor interp.  Its way faster, and we have to reprocesses the DEM anyway.
*   Doesn't seem like the sampling method made any difference as to reprocessesing need - see below.  


#### 2) ProcessSurfaceFlow.py - calculate Flowaccumulation and direction
*  Had to repeat the above hydrologic processing with the resampled DEM. Might not be worth doing it the first time. 
  *  pyGSFLOW processing can't handle the dem.  Need to do the full deal.
  *  I think that different interpolation methods are probably not worth the cost given that I had to repeat the processing.
*  Processing Steps in QGIS using SAGA:
  1. Fill Sinks -> needs: resampled dem; produces: filled dem
  2. Catchment Area -> needs: filled dem: produces: upslope accumulated area
  3. Channel Network -> needs: filled dem, upslope accumulated area (for initiation points); produces stream network (raster and shape)
    - initiation area greater than 5e5 works good 
  4. Burn Stream Network
    - epsilion 1.0 method [1] -> needs filled dem, stream network raster, flow direction raster
*  I then use the resampled, reprocessed dems in Q, to process with pygsflow.
*  Should probably due this with python SAGA API, but for now it is done with Q.
*  Flow Accumulation plot lots good now.

#### 3) ProcessWatersheds.py - get full watershed, and subwatersheds.
*  Drain points picked in QGIS - ElkCreekPourPoint.shp and Subsheds.shp in HydroProc.
*  Not sure I'll ever use, or how to use Subsheds yet.  Maybe it will be come clear later.

#### 4) Process Streams and Cascades
*  Changed the accumulated area threshold a bit - increased it - to keep the number of stream segments down
*  Added a minimum stream length of 10 cells to reduce the number of segment more.  
  *  I still have more segments than the tutorial example by a fair amount.  So, lets see if that is an issue
*  My number of cascades is less than the tutorial example.  Lets see how much of a problem that is.

#### 5) MODFLOW - time to build the subsuface!
*  Probably need to learn more about each package, SFR, UPW, UZF
  * Read up, but could always learn more
* only one layer for now, but next step is to add layers.

#### 6) MODFLOW SFR
*  Had issues, and went down a worm hole.  However, if I use the development version, the SFR rounting working.  Bottom line.  Use dev

#### MODFLOW SIMULATIONS
* I think for now it could be useful just to run moflow simulations using an infiltration rate and evapotranspiration calculated externally.  

#### 7) SOIL
*  3/3/23 - Need to figure out how to use the ssurgo data set.  Think I need to read the raster in to python, then I can make 
    other rasters using a join on the mukey.  The main issue is now finding the correct columns in the correct tables.






