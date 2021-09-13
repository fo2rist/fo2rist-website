#!/usr/local/bin/python3
"""
Generic functions for AirTable data access.
"""

import json
import urllib.request
import urllib.parse

def airtable_get_items(api_key, base_id, table_name, params):
    """
    Get items from table by given search params.
    For params see https://airtable.com/api
    """
    encoded_params = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"https://api.airtable.com/v0/{base_id}/{table_name}?{encoded_params}")
    req.add_header('Authorization', 'Bearer ' + api_key)
    
    with urllib.request.urlopen(req) as response:
        data = response.read().decode('utf-8')
        parsed_data = json.loads(data)
        return parsed_data['records']
