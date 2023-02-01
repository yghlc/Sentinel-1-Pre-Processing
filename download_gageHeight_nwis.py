#!/usr/bin/env python
# Filename: download_hydro.py 
"""
introduction: download daily mean gage height observations from  NWIS: https://nwis.waterdata.usgs.gov/nwis
             using a forked PyGeoHydro (https://github.com/yghlc/pygeohydro)

             Gage height, feet (Mean)

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 31 January, 2023
"""

import os, sys
from optparse import OptionParser
from datetime import datetime

import genTools
import vector_tools

import pandas as pd

def save_xlsx_table(dataframe,save_path):
    with pd.ExcelWriter(save_path) as writer:
        dataframe.to_excel(writer, sheet_name='data')
        print('save table to %s' % os.path.abspath(save_path))

def test_download_one_site():
    site_no = '08068720'
    dates_str = ("2017-08-16", "2017-09-13")

    from pygeohydro import NWIS
    nwis = NWIS()

    out_table = nwis.get_gageheight([site_no],dates_str)
    # print(out_table)
    out_table.reset_index(inplace=True)
    out_table['index'] = out_table['index'].astype(str)
    save_xlsx_table(out_table,site_no+'gageHeight.xlsx')



def download_gage_height(extent_shp, save_path, cache_dir, dates_str=("2017-08-16", "2017-09-13")):
    ext_polys = vector_tools.read_shape_gpd_to_NewPrj(extent_shp,'EPSG:4326')
    if len(ext_polys) != 1:
        raise ValueError('currently, only support one polygon')
    bounds = [item.bounds for item in ext_polys][0]
    # minx, miny, maxx, maxy = poly.bounds
    # bounds = (-95.00715306114322, 30.0368774601673, -94.42042753827869, 30.454254427946868)
    print(bounds)

    from pygeohydro import NWIS

    nwis = NWIS()
    # codes = nwis.get_parameter_codes("%gage%")
    # save_xlsx_table(codes,'gage_codes.xlsx')

    query = {
        "bBox": ",".join(f"{b:.06f}" for b in bounds),
        "hasDataTypeCd": "dv",
        "outputDataTypeCd": "dv",
    }
    #  info_box is GeoDataframe
    info_box = nwis.get_info(query)
    # print(info_box)

    site_file = os.path.splitext(os.path.basename(save_path))[0] +'_info_box.gpkg'
    info_box.to_file(site_file, driver='GPKG')
    print('save site locations to %s'%site_file)

    dates = tuple([datetime.strptime(item, '%Y-%m-%d') for item in dates_str])

    stations = info_box[(info_box.begin_date <= dates[0]) & (info_box.end_date >= dates[1])].site_no.tolist()

    # gageHeight is a dateframe
    gageHeight = nwis.get_gageheight(stations, dates_str)
    # print(qobs.attrs)
    gageHeight.reset_index(inplace=True)
    # for key in qobs.keys():
    #     print(key)
    # print(qobs)
    gageHeight['index'] = gageHeight['index'].astype(str)
    # plot.signatures(qobs)
    save_xlsx_table(gageHeight,save_path)



def main(options, args):
    extent_shp = args[0]
    assert os.path.isfile(extent_shp), 'File not exists'

    save_path = options.save_path
    cache_dir = options.cache_dir

    if save_path is None:
        file_name = os.path.splitext(os.path.basename(extent_shp))[0]
        save_path = os.path.join(os.getcwd(), file_name + '_hydro.xlsx')
    else:
        save_path = os.path.abspath(save_path)

    start_date = options.start_date
    end_date = options.end_date

    print(datetime.now(), 'download daily mean gage height (feet), \nwill save to %s' % (save_path))
    # if os.path.isfile(save_path):
    #     print("%s already exists, skip" % save_path)
    #     return

    if cache_dir is None:
        cache_dir = os.path.expanduser('~/hydro')
    if os.path.isdir(cache_dir) is False:
        os.makedirs(cache_dir)

    # test_download_one_site()
    download_gage_height(extent_shp, save_path, cache_dir, dates_str=(start_date, end_date))



if __name__ == "__main__":

    usage = "usage: %prog [options] extent_shp "
    parser = OptionParser(usage=usage, version="1.0 2023-01-31")
    parser.description = 'Introduction: download daily mean gage height from NWIS'

    parser.add_option("-d", "--save_path",
                      action="store", dest="save_path",
                      help="the path for saving a DEM file")

    parser.add_option("-s", "--start_date",default="2017-08-16",
                      action="store", dest="start_date",
                      help="start date for inquiry, with format year-month-day, e.g., '2017-08-16'")

    parser.add_option("-e", "--end_date",default="2017-09-13",
                      action="store", dest="end_date",
                      help="the end date for inquiry, with format year-month-day, e.g., 2017-09-13")

    parser.add_option("-a", "--cache_dir",
                      action="store", dest="cache_dir",
                      help="the cache directory")

    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)

    main(options, args)