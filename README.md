# Sentinel-1-Pre-Processing

This repository contains the scripts to download Sentinel-1 data from the Alaska SAR Faciity (ASF)
archive using ASF's API service (ASF_API) and a script to perform radiometric terrain correction on 
the Ground Range Detected (GRD) data (RTC_vX.py). Instructions and sample input files are provided in 
each folder. 


### Install 
```
   # pre-processing (GDAL will automatically be installed)
   conda create -n sar python=3.9
   conda activate sar
   conda install -c conda-forge asf_search
   conda install -c conda-forge geopandas   
   conda install -c conda-forge rasterio
   
   ### install SNAP
   # SNAP: install SNAP (https://step.esa.int/main/download/snap-download/)
   # Note: A SNAP update may be necessary, even after a fresh install. 
   # E.g. /local_path_to_snap/snap/bin/snap --nosplash --nogui --modules --update-all
   
   ### Download DEM 
   # pip install elevation    # to download SRTM https://github.com/bopen/elevation (no need)
   pip install wget  
   
```
