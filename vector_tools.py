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

def read_vector_bound(shp_path):
    shapefile = gpd.read_file(shp_path)
    polygons = shapefile.geometry.values
    if len(polygons) != 1:
        raise ValueError('only support one polygon')
    return polygons[0].bounds


def check_remove_None_geometries(geometries, gpd_dataframe, file_path=None):
    # Missing and empty geometries, find None geometry, then remove them
    # https://geopandas.org/en/stable/docs/user_guide/missing_empty.html

    # check None in geometries:
    # gpd_dataframe = gpd.read_file(polygon_shp)
    # geometries = shapefile.geometry.values

    idx_list = [ idx for idx, polygon in enumerate(geometries) if polygon is None]
    if len(idx_list) > 0:
        message = 'Warning, %d None geometries, will be removed'%len(idx_list)
        if file_path is not None:
            message += ', file path: %s'%file_path
        for idx in idx_list:
            gpd_dataframe.drop(idx, inplace=True)
            # geometries.drop(idx,inplace=True)     # not working
        print(message)

    # return geometries again after droping some rows
    return gpd_dataframe.geometry.values

def fix_invalid_polygons(polygons, buffer_size = 0.000001):
    '''
    fix invalid polygon by using buffer operation.
    :param polygons: polygons in shapely format
    :param buffer_size: buffer size
    :return: polygons after checking invalidity
    '''
    invalid_polygon_idx = []
    for idx in range(0,len(polygons)):
        if polygons[idx].is_valid is False:
            invalid_polygon_idx.append(idx + 1)
            polygons[idx] = polygons[idx].buffer(buffer_size)  # trying to solve self-intersection
    if len(invalid_polygon_idx) > 0:
        print('Warning, polygons %s (index start from 1) in are invalid, fix them by the buffer operation '%(str(invalid_polygon_idx)))

    return polygons


def read_polygons_gpd(polygon_shp, b_fix_invalid_polygon = True):
    '''
    read polyogns using geopandas
    :param polygon_shp: polygon in projection of EPSG:4326
    :param no_json: True indicate not json format
    :return:
    '''

    shapefile = gpd.read_file(polygon_shp)
    polygons = shapefile.geometry.values

    # fix invalid polygons
    if b_fix_invalid_polygon:
        polygons = fix_invalid_polygons(polygons)

    return polygons

def is_field_name_in_shp(polygon_shp, field_name):
    '''
    check a attribute name is in the shapefile
    :param polygon_shp:
    :param field_name:
    :return:
    '''
    shapefile = gpd.read_file(polygon_shp)
    if field_name in shapefile.keys():
        return True
    else:
        return False

def add_attributes_to_shp(shp_path, add_attributes,save_as=None,format='ESRI Shapefile'):
    '''
    add attbibutes to a shapefile
    :param shp_path: the path of shapefile
    :param add_attributes: attributes (dict)
    :return: True if successful, False otherwise
    '''

    shapefile = gpd.read_file(shp_path)
    # print(shapefile.loc[0])   # output the first row

    # get attributes_names
    org_attribute_names = [ key for key in  shapefile.loc[0].keys()]
    # print(org_attribute_names)
    for key in add_attributes.keys():
        if key in org_attribute_names:
            print('warning, field name: %s already in table '
                                       'this will replace the original value'%(key))
        shapefile[key] = add_attributes[key]

    # print(shapefile)
    # save the original file
    if save_as is not None:
        return shapefile.to_file(save_as, driver=format)
    else:
        return shapefile.to_file(shp_path, driver=format)

def read_polygons_attributes_list(polygon_shp, field_nameS, b_fix_invalid_polygon = True):
    '''
    read polygons and attribute value (list)
    :param polygon_shp:
    :param field_nameS: a string file name or a list of field_name
    :return: Polygons and attributes
    '''
    shapefile = gpd.read_file(polygon_shp)
    polygons = shapefile.geometry.values
    # check None
    polygons = check_remove_None_geometries(polygons,shapefile,polygon_shp)

    # fix invalid polygons
    if b_fix_invalid_polygon:
        polygons = fix_invalid_polygons(polygons)

    # read attributes
    if isinstance(field_nameS,str): # only one field name
        if field_nameS in shapefile.keys():
            attribute_values = shapefile[field_nameS]
            return polygons, attribute_values.tolist()
        else:
            print('Warning: %s not in the shape file, get None' % field_nameS)
            return polygons, None
    elif isinstance(field_nameS,list):  # a list of field name
        attribute_2d = []
        for field_name in field_nameS:
            if field_name in shapefile.keys():
                attribute_values = shapefile[field_name]
                attribute_2d.append(attribute_values.tolist())
            else:
                print('Warning: %s not in the shape file, get None' % field_nameS)
                attribute_2d.append(None)
        return polygons, attribute_2d
    else:
        raise ValueError('unknown type of %s'%str(field_nameS))


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