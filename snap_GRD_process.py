#!/usr/bin/env python
# Filename: snap_GRD_process.py 
"""
introduction: Apply Orbit File, Remove GRD Border Noise, Calibration, Speckle Filter, and Terrain Correction to SNAP
"""

import os,sys
from optparse import OptionParser
import glob
from datetime import datetime
import time

import RTC.RTC_v3 as RTC_v3

from genTools import read_dict_from_txt_json

def get_grd_file_list(file_or_dir):
    if os.path.isdir(file_or_dir):
        GRD_files = glob.glob(os.path.join(file_or_dir, '*GRDH*.zip'))
    else:
        with open(file_or_dir,'r') as f_obj:
            GRD_files = [line.strip() for line in f_obj.readlines()]
    return GRD_files

def GRD_file_preProcessing(grd_list,save_dir,pixel_size, dem_file=None):
    t0 = time.time()
    total_count = len(grd_list)
    for idx, grd in enumerate(grd_list):
        t1 = time.time()
        print(datetime.now(),'Processing GRD File %s / %s' % (idx + 1, total_count))
        granule = os.path.basename(grd).split('.')[0]
        Output_Directory = RTC_v3.output_dir(save_dir, granule)
        if len(glob.glob(os.path.join(Output_Directory, '*VV*'))) == 0:
            # orbit correction
            Orbit_Correction = RTC_v3.applyOrbit(Output_Directory, grd, granule)
            # border noise removal
            Border_Noise_Removal = RTC_v3.applyremovebordernoise(Output_Directory, Orbit_Correction, granule)
            # Calibration to sigma nought
            Calibration = RTC_v3.applyCal(Output_Directory, Border_Noise_Removal, granule)
            # speckle filter
            Speckle_Filter = RTC_v3.applySpeckle(Output_Directory, Calibration, granule)
            # terrain correction
            dem_file = ' ' if dem_file is None else dem_file
            Terrain_Correction = RTC_v3.applyTC(Output_Directory, Speckle_Filter, granule, pixel_size, dem_file)
            # write out data to geotiffs VV and VH
            Sigma0_directory = Terrain_Correction.replace('.dim', '.data')
            RTC_v3.Sigma0_FF_2_gtif(Output_Directory, Sigma0_directory, granule)
            RTC_v3.clean_dirs(Output_Directory, os.path.join(save_dir, 'final'))
        else:
            print('%s already has output files...skipping' % (grd))
        print(datetime.now(), 'Complete, took %s seconds' % (time.time() - t1))
    total_time = time.time() - t0
    print(datetime.now(),'Process complete, took %s seconds' % (total_time))



def main(options, args):
    grd_file_list =get_grd_file_list(args[0])
    save_dir = options.save_dir
    pixel_size = options.save_pixel_size
    dem_file = options.elevation_file
    setting_json = options.env_setting

    env_setting = read_dict_from_txt_json(setting_json)
    RTC_v3.baseSNAP = env_setting['snap_bin_gpt']
    print(datetime.now(),'setting SNAP gpt:', RTC_v3.baseSNAP)
    RTC_v3.gdal_translate = env_setting['gdal_translate_bin']
    print(datetime.now(), 'gdal_translate:', RTC_v3.gdal_translate)

    GRD_file_preProcessing(grd_file_list, save_dir, pixel_size, dem_file=dem_file)



if __name__ == "__main__":

    usage = "usage: %prog [options] grd_files.txt or grd_directory "
    parser = OptionParser(usage=usage, version="1.0 2022-10-31")
    parser.description = 'Introduction: Pre-processing SAR GRD files, input a txt file contains file list or a directory containing files'

    parser.add_option("-d", "--save_dir",
                      action="store", dest="save_dir",default='asf_data',
                      help="the folder to save pre-processed results")

    parser.add_option("-p", "--save_pixel_size",
                      action="store", dest="save_pixel_size",type=float, default='10.0',
                      help="the spatial resolution of output raster")

    parser.add_option("-e", "--elevation_file",
                      action="store", dest="elevation_file",
                      help="DEM file used for terrain correction, if not set, will use SRTM 1 sec ")

    parser.add_option("-s", "--env_setting",
                      action="store", dest="env_setting", default='env_setting.json',
                      help=" the setting of software environment  ")


    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)

    main(options, args)


