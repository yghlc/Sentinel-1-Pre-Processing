#!/usr/bin/env python
# Filename: download3DEP.py 
"""
introduction:

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 30 January, 2023
"""

import os, sys
from optparse import OptionParser
from datetime import datetime
import random

import vector_tools

def download_3DEP_cmd(extent_shp, save_path, cache_dir, resolution=10):
    if os.path.isfile(save_path):
        print('%s already exist, skip downloading'%save_path)
        return

    # checking if 'id' and 'res' are in the shapefile
    if vector_tools.is_field_name_in_shp(extent_shp,'id') is False:
        add_att = {'id': random.randint(10, 1000000) }
        vector_tools.add_attributes_to_shp(extent_shp,add_att)
        print('Added id (%d) to %s'%(add_att['id'], extent_shp))
    if vector_tools.is_field_name_in_shp(extent_shp, 'res') is False:
        add_att = {'res': float(resolution)}
        vector_tools.add_attributes_to_shp(extent_shp, add_att)
        print('Added res (%f) to %s' % (add_att['res'], extent_shp))

    polygons, attributes = vector_tools.read_polygons_attributes_list(extent_shp, ['id','res'])
    if len(polygons) != 1:
        raise ValueError('Currently, only support one polygon')

    id = attributes[0][0]
    dem_nc_file = os.path.join(cache_dir, '%d.nc'%id )

    # using py3dep to download DEM
    cmd_str = 'py3dep geometry %s  -l DEM -s %s'%(extent_shp,cache_dir)
    res = os.system(cmd_str)
    if res != 0:
        sys.exit(res)

    # convert to geotiff
    # res = attributes[0][1]
    cmd_str = 'gdal_translate %s %s'%(dem_nc_file,save_path)
    res = os.system(cmd_str)
    if res != 0:
        sys.exit(res)


def main(options, args):
    extent_shp = args[0]
    assert os.path.isfile(extent_shp), 'File not exists'

    save_path = options.save_path
    cache_dir = options.cache_dir
    res = options.resolution
    if save_path is None:
        file_name = os.path.splitext(os.path.basename(extent_shp))[0]
        save_path = os.path.join(os.getcwd(), file_name + '_DEM.tif')
    else:
        save_path = os.path.abspath(save_path)
    print(datetime.now(), 'download 3DEP, \nwill save to %s' % (save_path))  # at resolution of %lf meters,
    if os.path.isfile(save_path):
        print("%s already exists, skip" % save_path)
        return

    if cache_dir is None:
        cache_dir = os.path.expanduser('~/elevation')
    if os.path.isdir(cache_dir) is False:
        os.makedirs(cache_dir)

    download_3DEP_cmd(extent_shp, save_path, cache_dir, resolution=res)



if __name__ == "__main__":

    usage = "usage: %prog [options] extent_shp "
    parser = OptionParser(usage=usage, version="1.0 2023-01-30")
    parser.description = 'Introduction: download 3DEP elevation, in the extent_shp, should contain "id", and "res" '

    parser.add_option("-d", "--save_path",
                      action="store", dest="save_path",
                      help="the path for saving a DEM file")

    parser.add_option("-r", "--resolution",
                      action="store", dest="resolution", default=10,
                      help="the resolution for the saving DEM file")

    parser.add_option("-a", "--cache_dir",
                      action="store", dest="cache_dir",
                      help="the cache directory")


    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)

    main(options, args)