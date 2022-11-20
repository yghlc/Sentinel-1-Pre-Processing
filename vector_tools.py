#!/usr/bin/env python
# Filename: vector_tools.py 
"""
introduction:

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 31 October, 2022
"""

import geopandas as gpd
from packaging import version

from shapely import geometry
import re
import pandas as pd

def read_shape_gpd_to_NewPrj(shp_path, prj_str):
    '''
    read polyogns using geopandas, and re-project to a projection if necessary.
    :param shp_path:
    :param prj_str:  project string, like EPSG:4326
    :return:
    '''
    shapefile = gpd.read_file(shp_path)
    # print(shapefile.crs)

    # shapefile  = shapefile.to_crs(prj_str)
    if version.parse(gpd.__version__)  >= version.parse('0.7.0'):
        shapefile = shapefile.to_crs(prj_str)
    else:
        shapefile  = shapefile.to_crs({'init':prj_str})
    # print(shapefile.crs)
    polygons = shapefile.geometry.values

    return polygons

def save_shape_to_files(data_frame, geometry_name, wkt_string, save_path,format='ESRI Shapefile'):
    '''
    :param data_frame: include polygon list and the corresponding attributes
    :param geometry_name: dict key for the polgyon in the DataFrame
    :param wkt_string: wkt string (projection)
    :param save_path: save path
    :param format: use ESRI Shapefile or "GPKG" (GeoPackage)
    :return:
    '''
    # data_frame[geometry_name] = data_frame[geometry_name].apply(wkt.loads)
    poly_df = gpd.GeoDataFrame(data_frame, geometry=geometry_name)
    poly_df.crs = wkt_string # or poly_df.crs = {'init' :'epsg:4326'}
    poly_df.to_file(save_path, driver=format)

    return True

def polygon_wkt_string_2_shapefile(wkt_str, save_path):
    all_digits = re.findall('\-?\d+\.\d+',wkt_str)
    # print(all_digits)
    count = int(len(all_digits)/2)
    points = [(float(all_digits[2*idx]), float(all_digits[2*idx+1])) for idx in range(count) ]
    print(points)
    poly = geometry.Polygon(points)
    print(poly.wkt)

    # save to file
    save_pd = pd.DataFrame({'Polygon':[poly]})
    geometry_name = 'Polygon'
    wkt_string = 'EPSG:4326'
    save_shape_to_files(save_pd, geometry_name, wkt_string, save_path, format='ESRI Shapefile')


def test_polygon_wkt_string_2_shapefile():
    # mid west
    wkt = 'POLYGON((-98.23974609375 43.34116005412307, -98.23974609375 38.85682013474361, -92.94433593749 38.85682013474361, -92.94433593749 43.34116005412307, -98.23974609375 43.34116005412307))'
    save_path = 'mid_west_ext.shp'
    polygon_wkt_string_2_shapefile(wkt, save_path)

if __name__ == '__main__':
    pass