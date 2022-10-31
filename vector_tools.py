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


if __name__ == '__main__':
    pass