#!/usr/bin/env python
# Filename: downloadSRTM.py 
"""
introduction: download SRTM using elevation: https://github.com/bopen/elevation

install: pip install elevation

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 02 December, 2022
"""

import os, sys
from optparse import OptionParser
from datetime import datetime

import vector_tools
import elevation

def download_SRTM_cmd(extent_shp,save_path):
    cmd_str = "eio clip -o %s --reference %s"%(save_path,extent_shp)
    res = os.system(cmd_str)
    if res != 0:
        sys.exit(1)

def download_SRTM(extent_shp,save_path,cache_dir,b_clean=False):
    bounds = vector_tools.read_vector_bound(extent_shp)
    # print(bounds)
    gen_bounds = elevation.datasource.build_bounds(bounds, margin='0')
    if cache_dir is None:
        cache_dir = os.path.expanduser('~/elevation')
    datasource_root = elevation.datasource.seed(cache_dir=cache_dir,bounds=gen_bounds, product='SRTM1', max_download_tiles=3000)
    elevation.datasource.do_clip(datasource_root, gen_bounds, save_path)
    if b_clean:
        elevation.clean()

def main(options, args):
    extent_shp = args[0]
    assert os.path.isfile(extent_shp)

    save_path = options.save_path
    b_clean = options.clean
    cache_dir = options.cache_dir
    if save_path is None:
        file_name = os.path.splitext(os.path.basename(extent_shp))[0]
        save_path = os.path.join(os. getcwd(),file_name + '_DEM.tif')
    else:
        save_path = os.path.abspath(save_path)
    print(datetime.now(), 'download SRTM1, \nwill save to %s'%save_path)

    # download_SRTM_cmd(extent_shp,save_path)
    download_SRTM(extent_shp, save_path,cache_dir,b_clean=b_clean)

if __name__ == "__main__":

    usage = "usage: %prog [options] extent_shp "
    parser = OptionParser(usage=usage, version="1.0 2022-12-02")
    parser.description = 'Introduction: download SRTM  '

    parser.add_option("-d", "--save_path",
                      action="store", dest="save_path",
                      help="the path for saving a DEM file")

    parser.add_option("-a", "--cache_dir",
                      action="store", dest="cache_dir",
                      help="the cache directory")

    parser.add_option("-c", "--clean",
                      action="store_true", dest="clean", default=False,
                      help="clean up stale temporary files and fix the cache in the event of a server error")


    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)

    main(options, args)

