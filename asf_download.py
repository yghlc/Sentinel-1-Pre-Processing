#!/usr/bin/env python
# Filename: asf_download.py 
"""
introduction: download data from The Alaska Satellite Facility (ASF)

add time: 31 October, 2022
"""

import os,sys
from optparse import OptionParser
from datetime import datetime
import time

from vector_tools import read_shape_gpd_to_NewPrj

import asf_search as asf

def shapefile_to_ROIs_wkt(shp_path):
    polygons = read_shape_gpd_to_NewPrj(shp_path,'EPSG:4326')  # lat, lon
    if len(polygons) < 1:
        raise ValueError('No polygons in %s'%shp_path)
    ROIs_wkt = [str(p) for p in polygons ]
    return ROIs_wkt


def download_data_from_asf(idx,roi_count,roi_wkt, save_dir, start_date, end_date, processingLevel, username, password,
                           beamMode='IW',platform=asf.PLATFORM.SENTINEL1 ):
    ## ROI
    print(datetime.now(),'Searching... ... ...')
    if isinstance(platform, list):
        platform_list = platform
    else:
        platform_list = [platform]

    results = asf.geo_search(platform=platform_list, intersectsWith=roi_wkt, start=start_date,
                             end=end_date,
                             beamMode=beamMode, processingLevel=processingLevel)
    print(datetime.now(),'Found %s results' % (len(results)))
    session = asf.ASFSession()
    session.auth_with_creds(username, password)
    print(datetime.now(),'Downloading... ... ...')

    if roi_count == 1:
        download_dir = save_dir
    elif roi_count > 1:
        download_dir = os.path.join(save_dir,'roi_%d'%idx)
    else:
        raise ValueError('There is zero ROI')
    if not os.path.isdir(download_dir):
        os.makedirs(download_dir)

    results.download(path=download_dir, session=session)  # download results to a path
    print(datetime.now(),'Finished Download')

    ## Save results to an output log
    log_filename = os.path.join(download_dir, "download_log.txt")
    print(' ')
    print(datetime.now(),'Saving log results to ', log_filename)
    stdoutOrigin = sys.stdout
    # sys.stdout = open (download_dir + region + "_download_log.txt", "w")
    sys.stdout = open(log_filename, "w")
    print(results)
    sys.stdout.close()
    sys.stdout = stdoutOrigin

def main(options, args):
    extent_shp = args[0]
    assert os.path.isfile(extent_shp)

    save_dir = options.save_dir
    start_date = options.start_date
    end_date = options.end_date
    user_name = options.username
    password = options.password

    print(datetime.now(), 'download data from ASF, start_date: %s, end_date: %s, user: %s, \nwill save to %s'%(start_date,end_date,user_name,save_dir))

    processingLevel = 'GRD_HD'

    # shapefile to  ROI
    ROIs_wkt = shapefile_to_ROIs_wkt(extent_shp)
    for idx, roi_wkt in enumerate(ROIs_wkt):
        # download data
        download_data_from_asf(idx, len(ROIs_wkt), roi_wkt, save_dir, start_date, end_date, processingLevel, user_name,
                               password,
                               beamMode='IW', platform=asf.PLATFORM.SENTINEL1)




if __name__ == "__main__":

    usage = "usage: %prog [options] extent_shp "
    parser = OptionParser(usage=usage, version="1.0 2022-10-31")
    parser.description = 'Introduction: download data from the Alaska Satellite Facility  '

    parser.add_option("-d", "--save_dir",
                      action="store", dest="save_dir",default='asf_data',
                      help="the folder to save downloaded data")

    parser.add_option("-s", "--start_date",default='2018-04-30',
                      action="store", dest="start_date",
                      help="start date for inquiry, with format year-month-day, e.g., 2018-05-23")
    parser.add_option("-e", "--end_date",default='2018-06-30',
                      action="store", dest="end_date",
                      help="the end date for inquiry, with format year-month-day, e.g., 2018-05-23")

    parser.add_option("-u", "--username",
                      action="store", dest="username",
                      help="Earth Data account")
    parser.add_option("-p", "--password",
                      action="store", dest="password",
                      help="password for the earth data account")


    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)

    main(options, args)
