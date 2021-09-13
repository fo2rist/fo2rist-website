#!/usr/local/bin/python3

import re
import os
from datetime import date
from operator import itemgetter
from podcast_utils import *

#region Auphonic IDs
PRESET_MULTITRACK_WITH_TRACKS = "5RfARu2gxMJJZj3tmxWd8U"
PRESET_MULTITRACK_EMPTY = "f34aLbvfmPqKjYgGi8qs9E"
GOOGLE_DRIVE_SERVICE_ID = "uKrCoE47igevybFq73HrQE"
#endregion

def escape(s):
    """Replace quotes with escaped quotes for JSON"""
    return s.replace('"', '\\"')

def create_auphonic_production(episode_number, episode_title, episode_comment, episode_description, timings, links, briefs, recording_files):
    """Create new production on Auphonic platform"""

    # chapters with optional links. Format {"start": "00:00:00", "title": "Start Chapter", "url": "http://auphonic.com"}
    #  assume we don't start any theme after 1h
    chapters_for_metadata  = \
            ["""{"start": "00:00:00", "title": "Интро"}"""] +\
            [f"""{{"start": "00:{t}", "title": "{escape(d)}", "url": "{l}"}}""" for (t,d,l) in zip(
                timings, 
                map(lambda s: re.sub('^!!', '', s), briefs),
                list( map(itemgetter(0), links)))]
    chapters_json = "[\n" + ",\n".join(chapters_for_metadata) + "\n]"

    # Create production JSON
    files_json_list = []
    for file_name in recording_files:
        track_id = HOST_DIMA if "fo2" in file_name else\
                HOST_YULIA if "yul" in file_name else\
                HOST_GEORGE if "geo" in file_name else\
                re.sub(r".*--.*--", "", file_name).replace(".mp3", "")
        files_json_list.append(
            f"""{{
                "service": "{GOOGLE_DRIVE_SERVICE_ID}",
                "id": "{track_id}",
                "input_file": "{file_name}",
                "type": "multitrack",
                "algorithms": {{"denoise": true, "hipfilter": true, "backforeground": "foreground"}}
            }}""")
    files_json = ", ".join(files_json_list)

    production_json = f"""{{
            "action": "save",
            "preset": "{PRESET_MULTITRACK_EMPTY}",
            "metadata": {{
                "title": "{escape(episode_title)}",
                "track": {episode_number},
                "subtitle": "{escape(episode_comment)}",
                "summary": "{escape(episode_description)}",
                "year": {date.today().year},
                "append_chapters": false
            }},
            "chapters": {chapters_json},
            "multi_input_files": [{files_json}],
            "output_basename": "{build_episode_base_file_name(episode_number)}",
            "is_multitrack": true
        }}"""

    # create production on auphonic
    create_production_command = f"""
    curl -X POST https://auphonic.com/api/productions.json \\
        -H "Content-Type: application/json" \\
        -u fo2rist:wTi3ZhDP8Pauphonic \\
        -d '{production_json}'
    """
    print(create_production_command)
    os.system(create_production_command)
