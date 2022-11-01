#!/usr/bin/env python
# Filename: genTools.py 
"""
introduction:
add time: 01 November, 2022
"""

import os
import json

def read_dict_from_txt_json(file_path):
    if os.path.getsize(file_path) == 0:
        return None
    with open(file_path) as f_obj:
        data = json.load(f_obj)
        return data

if __name__ == '__main__':
    pass