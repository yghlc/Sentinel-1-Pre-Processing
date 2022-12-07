#!/bin/bash

# Exit immediately if a command exits with a non-zero status. E: error trace
set -eE -o functrace

# download Sentinel-1 data
down_py=asf_download.py
ext_shp=/data/flooding_area/Houston/extent_image_valid/houston_valid_image_extent.shp
save_dir=/data/flooding_area/test_docker_containers/Houston
s_date=2017-08-29
e_date=2017-08-30
username=$(awk '/urs.earthdata.nasa.gov/{getline; print $2}' /home/user/.netrc)
password=$(awk '/urs.earthdata.nasa.gov/{getline; getline; print $2}' /home/user/.netrc)
${down_py} ${ext_shp} -d ${save_dir}/sentinel-1  -s ${s_date} -e ${e_date} -u ${username} -p ${password}

# Apply Orbit File, Remove GRD Border Noise, Calibration, Speckle Filter, and Terrain Correction
rtc_py=snap_GRD_process.py
outdir=${save_dir}/pre-processed
${rtc_py} ${save_dir}/sentinel-1  -d ${outdir} -t /tmp

