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
# import elevation
import math

# use ~/.netrc for user/password
import os
# import wget
import requests
from netrc import netrc

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

def srtm_tiles_download(tile_list, cache_dir):
    # download SRTM tiles:
    # ref: https://github.com/ab-natcap/idb-scripts/blob/a1dcb89fe741ca1e737c59614e308ae49501ad08/srtm_download.py

    # Set up authentication using .netrc file
    urs = 'urs.earthdata.nasa.gov'  # Address to call for authentication
    netrcDir = os.path.expanduser("~/.netrc")
    user = netrc(netrcDir).authenticators(urs)[0]
    passwd = netrc(netrcDir).authenticators(urs)[2]

    srtm_url = 'https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/2000.02.11/'
    download_tiles = []
    for file in tile_list:
        save_tile = os.path.join(cache_dir,file)
        if os.path.isfile(save_tile):
            print('%s already exist'%save_tile)
            download_tiles.append(file)
            continue
        file_url = "{}{}".format(srtm_url, file)
        # wget.download(file_url, file)  # using requests instead (below)

        print('Beginning file download with requests {}'.format(file_url))
        # Create and submit request and download file
        with requests.get(file_url, stream=True, auth=(user, passwd)) as response:
            if response.status_code != 200:
                print("{} not downloaded. The tile is not available OR your username and password is incorrect in {}".
                      format(file,netrcDir))
            else:
                response.raw.decode_content = True
                content = response.raw
                with open(save_tile, 'wb') as d:
                    while True:
                        chunk = content.read(16 * 1024)
                        if not chunk:
                            break
                        d.write(chunk)
                print('Downloaded file: {}'.format(file))
                download_tiles.append(file)

    return download_tiles

def process_srtm_tiles(cache_dir, tile_list, save_path):
    if os.path.isfile(save_path):
        print('warning, %s exists, skip'%save_path)
        return False
    # unpack
    tile_paths = [os.path.join(cache_dir, item) for item in tile_list ]
    curr_dir = os.getcwd()
    os.chdir(cache_dir)
    for tile in tile_paths:
        if os.path.isfile(tile) is False:
            print('warning, %s does not exist'%tile)
            continue
        cmd_str = 'unzip %s'%tile
        res = os.system(cmd_str)
        if res != 0:
            sys.exit(1)

    # merge
    cmd_str = 'gdal_merge.py -o %s -n -32768 -a_nodata -32768  *.hgt'%save_path

    res = os.system(cmd_str)
    if res != 0:
        sys.exit(1)

    os.system('rm *.hgt')
    os.chdir(curr_dir)


def extent_to_1degree_tiles(poly):
    minx, miny, maxx, maxy = poly.bounds  # (minx, miny, maxx, maxy)
    x_list = [ item for item in range(math.floor(minx), math.ceil(maxx)) ]
    y_list = [ item for item in range(math.floor(miny), math.ceil(maxy)) ]
    # N15W086.SRTMGL1.hgt.zip
    tiles = []
    for y in y_list:
        lat_str = str(abs(y)).zfill(2)
        lat_str = 'N'+ lat_str if y > 0 else 'S'+lat_str
        for x in x_list:
            lon_str = str(abs(x)).zfill(3)
            lon_str = 'E' + lon_str if x > 0 else 'W' + lon_str
            tiles.append(lat_str+lon_str+'.SRTMGL1.hgt.zip')
    return tiles



def download_SRTM_url(extent_shp, save_path,cache_dir):
    '''
    Download SRTM 30m elevation tiles from URL
    :param extent_shp: shapefile
    :param save_path: output path
    :param cache_dir:
    :return:
    '''
    # shapefile to 1 by 1 degrees.
    ext_polys = vector_tools.read_shape_gpd_to_NewPrj(extent_shp,'EPSG:4326')
    if len(ext_polys) == 1:
        # create file names
        tiles = extent_to_1degree_tiles(ext_polys[0])
        download_tiles = srtm_tiles_download(tiles,cache_dir)
        if len(download_tiles) > 0:
            process_srtm_tiles(cache_dir, download_tiles, save_path)
        else:
            print('error, NO downloaded SRTM tiles')
    elif len(ext_polys) > 1:
        raise ValueError('currently, only support one polygon')
        pass
    else:
        raise ValueError('No extent polygons in %s'%extent_shp)

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
    if os.path.isfile(save_path):
        print("%s already exists, skip"%save_path)
        return

    if cache_dir is None:
        cache_dir = os.path.expanduser('~/elevation')
    else:
        cache_dir = os.path.abspath(cache_dir)
    if os.path.isdir(cache_dir) is False:
        os.makedirs(cache_dir)

    # download_SRTM_cmd(extent_shp,save_path)
    # download_SRTM(extent_shp, save_path,cache_dir,b_clean=b_clean)
    download_SRTM_url(extent_shp, save_path, cache_dir)

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

