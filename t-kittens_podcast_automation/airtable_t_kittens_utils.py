#!/usr/local/bin/python3
"""
High level T-Kittens AirTable database access functions.
For details see https://airtable.com/appZGxPKp1pgzNTiw/api/docs
"""

import os
from dotenv import load_dotenv
from airtable_utils import airtable_get_item, airtable_get_items

load_dotenv()

# AirTable API key is stored in the .env file
__api_key = os.getenv('AIRTABLE_API_KEY')
# T-Kittens AirTable database ID
__base_id = 'appZGxPKp1pgzNTiw'

# Json fields and table columns
__FIELDS_KEY = 'fields'
EPISODE_N = 'N'
ANCHOR_LINK = 'Published URL'
BRIEFS = 'Short Description'
DATE = 'Date'
DESCRIPTIONS = 'Full Description'
HOSTS = 'Hosts'
LINKS = 'Links'
NEWS = 'News'
NAME = 'Name'
AUTHOR = 'Author'
TIMING = 'Timing'

def get_last_episode() -> dict:
    """Get last Episode record as Airtable's JSON."""
    # Sample params for Episodes: {"sort[0][field]": "N", "sort[0][direction]": "desc", "maxRecords": 1}
    params = {"sort[0][field]": "N", "sort[0][direction]": "desc", "maxRecords": 1}
    episodes = airtable_get_items(__api_key, __base_id, "Episodes", params)
    return episodes[0][__FIELDS_KEY]

def get_episode(episode_number: int) -> dict:
    """Get Episode record as Airtable's JSON."""
    params = {"filterByFormula": f"{{N}} = {episode_number}"}
    episodes = airtable_get_items(__api_key, __base_id, "Episodes", params)
    if len(episodes) == 0:
        raise LookupError(f"Episode {episode_number} not found")
    return episodes[0][__FIELDS_KEY]

def get_last_episode_number() -> int:
    last_episode = get_last_episode()
    return last_episode[EPISODE_N]

def get_news(episode_number: int) -> list[dict]:
    """Get News of given episode sorted by timing"""
    # Sample params for News: {"sort[0][field]": "Timing", "filterByFormula": "{Is last episode}"}
    params = {"sort[0][field]": TIMING, "filterByFormula": f"{{Episode}} = {episode_number}"}
    news = airtable_get_items(__api_key, __base_id, "News", params)
    return list(map(lambda record: record[__FIELDS_KEY], news))

def get_author_names(ids: list[str]) -> list[str]:
    """Get names of hosts by list of IDs in the same order."""
    return list(
        map(lambda id: airtable_get_item(__api_key, __base_id, "Authors", id)[__FIELDS_KEY][NAME], ids)
        )
