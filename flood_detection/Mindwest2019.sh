#!/bin/bash

# Exit immediately if a command exits with a non-zero status. E: error trace
set -eE -o functrace

# download Sentinel-1 data
down_py=~/codes/PycharmProjects/yghlc_Sentinel-1-Pre-Processing/asf_download.py
ext_shp=~/Data/flooding_area/midWest2019/extent/mid_west_ext.shp
save_dir=~/Data/tmp_data/flood_detection
s_date=2019-04-01
e_date=2019-04-30
username=$(awk '/urs.earthdata.nasa.gov/{getline; print $2}' ~/.netrc)
password=$(awk '/urs.earthdata.nasa.gov/{getline; getline; print $2}' ~/.netrc)
${down_py} ${ext_shp} -d ${save_dir}  -s ${s_date} -e ${e_date} -u ${username} -p ${password}


# Apply Orbit File, Remove GRD Border Noise, Calibration, Speckle Filter, and Terrain Correction
rtc_py=~/codes/PycharmProjects/yghlc_Sentinel-1-Pre-Processing/snap_GRD_process.py
outdir=${save_dir}/pre-processed
${rtc_py} all_zip.txt -d ${outdir}


## run flood detection
##fd_py=~/codes/PycharmProjects/yghlc_Sentinel-1-Flood-Detection/SAR_Flood_Detection_v02.py
##python ${fd_py} fd_houston_2017_inputs.txt
#fd_py=~/codes/PycharmProjects/yghlc_Sentinel-1-Flood-Detection/sar_flood_det.py
#water_mask=~/Data/global_surface_water/extent_epsg4326_houston/extent_100W_30_40N_v1_3_2020.tif
#fd_dir=${save_dir}/FD_results_v2
##img_list=one_VV_Sigma0_images.txt
##img_list=one_VH_Sigma0_images.txt
#img_list=VH_VV_Sigma0_images.txt
#${fd_py} ${img_list} --src_nodata=0.0 -w ${water_mask} -d ${fd_dir}  --verbose \
#	--process_num=4




