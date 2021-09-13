#!/usr/local/bin/python3
"""
High level T-Kittens AirTable database access functions.
For details see https://airtable.com/appZGxPKp1pgzNTiw/api/docs
"""

import os
from dotenv import load_dotenv
from airtable_utils import airtable_get_items

load_dotenv()

# AirTable API key is stored in the .env file
api_key = os.getenv('AIRTABLE_API_KEY')
# T-Kittens base ID
base_id = 'appZGxPKp1pgzNTiw'


def get_last_episode():
    """Get last Episode record as Airtable's JSON."""
    # Sample params for Episodes: {"sort[0][field]": "N", "sort[0][direction]": "desc", "maxRecords": 1}
    params = {"sort[0][field]": "N", "sort[0][direction]": "desc", "maxRecords": 1}
    episodes = airtable_get_items(api_key, base_id, "Episodes", params)
    return episodes[0]

def get_last_episode_number():
    last_episode = get_last_episode()
    return last_episode['fields']['N']

def get_last_news():
    """Get News records for the last Episode record sorted by timing as Airtable's JSON."""
    # Sample params for News: {"sort[0][field]": "Timing", "filterByFormula": "{Is last episode}"}
    params = {"sort[0][field]": "Timing", "filterByFormula": "{Is last episode}"}
    news = airtable_get_items(api_key, base_id, "News", params)
    return news
