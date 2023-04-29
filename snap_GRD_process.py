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

def GRD_file_preProcessing(grd_list,temp_dir,save_dir,pixel_size, dem_file=None):
    t0 = time.time()
    total_count = len(grd_list)
    for idx, grd in enumerate(grd_list):
        t1 = time.time()
        print(datetime.now(),'Processing GRD File %s / %s' % (idx + 1, total_count))
        granule = os.path.basename(grd).split('.')[0]
        final_save_dir = os.path.join(save_dir, 'final')
        if len(glob.glob(os.path.join(final_save_dir, granule + '*'))) == 0:
            Output_Directory = RTC_v3.output_dir(temp_dir, granule)
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
            RTC_v3.clean_dirs(Output_Directory, final_save_dir)
        else:
            print('%s already has output files...skipping' % (grd))
        print(datetime.now(), 'Complete, took %s seconds' % (time.time() - t1))
    total_time = time.time() - t0
    print(datetime.now(),'Process complete, took %s seconds' % (total_time))

def test_Sigma0_FF_2_gtif():
    Output_Directory = os.path.expanduser('~/Data/tmp_data/flood_detection/pre-processed/S1A_IW_GRDH_1SDV_20170829T002620_20170829T002645_018131_01E74D_D734_Processed')
    Sigma0_directory = os.path.join(Output_Directory,'S1A_IW_GRDH_1SDV_20170829T002620_20170829T002645_018131_01E74D_D734_OB_GBN_CAL_SP_TC.data')
    granule = 'S1A_IW_GRDH_1SDV_20170829T002620_20170829T002645_018131_01E74D_D734'
    RTC_v3.Sigma0_FF_2_gtif(Output_Directory, Sigma0_directory, granule)

def main(options, args):

    if args[0].endswith('.json'):
        input_dict = read_dict_from_txt_json(args[0])
        file_list_or_dir = input_dict['s1_zip_file_list_or_dir']
        grd_file_list = get_grd_file_list(file_list_or_dir)
        save_dir = input_dict['sar_images_save_dir']
        temp_dir = input_dict['temp_dir'] if 'temp_dir' in input_dict.keys() else save_dir
        pixel_size = input_dict['save_pixel_size']
        dem_file = input_dict['elevation_file'] if 'elevation_file' in input_dict.keys() else None
        setting_json = input_dict['env_setting'] if 'env_setting' in input_dict.keys() else 'env_setting.json'
    else:
        grd_file_list = get_grd_file_list(args[0])
        save_dir = options.save_dir
        temp_dir = options.temp_dir if options.temp_dir is not None else save_dir
        pixel_size = options.save_pixel_size
        dem_file = options.elevation_file
        setting_json = options.env_setting

    if os.path.isfile(setting_json):
        env_setting = read_dict_from_txt_json(setting_json)
        RTC_v3.baseSNAP = env_setting['snap_bin_gpt']
        print(datetime.now(),'setting SNAP gpt:', RTC_v3.baseSNAP)
        RTC_v3.gdal_translate = env_setting['gdal_translate_bin']
        print(datetime.now(), 'gdal_translate:', RTC_v3.gdal_translate)
    else:
        RTC_v3.baseSNAP = os.getenv('SNAP_BIN_GPT')
        if RTC_v3.baseSNAP is None:
            raise ValueError('SNAP_BIN_GPT is not in Environment Variables')
        RTC_v3.gdal_translate = os.getenv('GDAL_TRANSLATE_BIN')
        if RTC_v3.gdal_translate is None:
            raise ValueError('GDAL_TRANSLATE_BIN is not in Environment Variables')

    # test_Sigma0_FF_2_gtif()
    GRD_file_preProcessing(grd_file_list, temp_dir, save_dir, pixel_size, dem_file=dem_file)



if __name__ == "__main__":

    usage = "usage: %prog [options] grd_files.txt or grd_directory "
    parser = OptionParser(usage=usage, version="1.0 2022-10-31")
    parser.description = 'Introduction: Pre-processing SAR GRD files, input a txt file containing a file list or a directory containing files'

    parser.add_option("-d", "--save_dir",
                      action="store", dest="save_dir",default='asf_data',
                      help="the folder to save pre-processed results")

    parser.add_option("-t", "--temp_dir",
                      action="store", dest="temp_dir",
                      help="the temporal folder for saving intermediate data ")

    parser.add_option("-p", "--save_pixel_size",
                      action="store", dest="save_pixel_size",type=float, default='10.0',
                      help="the spatial resolution of output raster")

    parser.add_option("-e", "--elevation_file",
                      action="store", dest="elevation_file",
                      help="DEM file used for terrain correction, if not set, will use SRTM 1 sec ")

    parser.add_option("-s", "--env_setting",
                      action="store", dest="env_setting", default='env_setting.json',
                      help=" the setting of the software environment  ")


    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)

    main(options, args)


