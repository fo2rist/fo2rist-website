#!/usr/bin/python3

import os
import re
import shutil
from datetime import date
from operator import itemgetter
from os.path import join
from podcast_utils import *

def escape(s):
    """Replace quotes with escaped quotes for JSON"""
    return s.replace('"', '\\"')

#region Auphonic IDs
PRESET_MULTITRACK_WITH_TRACKS = "5RfARu2gxMJJZj3tmxWd8U"
PRESET_MULTITRACK_EMPTY = "f34aLbvfmPqKjYgGi8qs9E"
GOOGLE_DRIVE_SERVICE_ID = "uKrCoE47igevybFq73HrQE"
#endregion

#region metadata constants
EPISODE_PREFIX = "Выпуск "
#endregion

# Sanity check
assert_tkittens_podcast_folder()

# Locate recordings
episode_number = get_last_episode_number()
episode_folder = get_last_episode_folder_name()

try:
    recording_folder = get_recording_folder_path()
    recording_files = get_recording_file_names()
except FileNotFoundError as err:
    print(f"Recording folder for last episode doesn't exist: {err}")
    exit(0)

# Move single track recording to production folders
for file_name in recording_files:
    # Copy files to final Episode folder (primary storage)
    shutil.copyfile(
        join(recording_folder, file_name),
        join(episode_folder, file_name))
    
    # Copy files to Auphonic google drive files for production
    shutil.copyfile(
        join(recording_folder, file_name),
        join(DRIVE_AUPHONIC_FOLDER, file_name))

# Fetch data parts (description, timings, links)
date_regex = re.compile(r"DATE: (\d\d\d\d-\d\d?-\d\d?)")
timings_regex = re.compile(r"(\d?\d:\d\d) - .+")
links_regex = re.compile(r"LINKS_\d:\s+(.*)")
theme_briefs_regex = re.compile(r"THEME_\d_SHORT:\s+(.+)")
theme_descriptions_regex = re.compile(r"THEME_\d_FULL:\s+(.+)")
recording_date = ""
timings = []
links = []
briefs = []
descriptions = []
with open(join(episode_folder, DESCRIPTION_FILE_NAME)) as file:
    for line in file:
        if date_match := date_regex.match(line):
            recording_date = date_match[1]
        if timing_match := timings_regex.match(line):
            timings.append(timing_match[1])
        if link_match := links_regex.match(line):
            links.append(list(link_match[1].split(" ")))
        if brief_match := theme_briefs_regex.match(line):
            briefs.append(brief_match[1].strip())
        if description_match := theme_descriptions_regex.match(line):
            descriptions.append(description_match[1].strip())

# Validarte the metadata
if len(timings) != len(links)\
        or len(timings) != len(briefs)\
        or len(timings) != len(descriptions):
    print(f"Some metadata is missing!\nFiles {recording_files}\nTimings {timings}\nLinks {links}\nBriefs {briefs}\nDescriptions {descriptions}")
    exit(0)

# Generate metadata for production
# Title - episode number
episode_title = f"{EPISODE_PREFIX}{episode_number}"
# Comment - short list of themes, excluding themes starting with '!!'
episode_comment = ", ".join(
    list(filter(lambda s: not s.startswith('!!'), briefs)))
# Description - themes of each chapter in the list
episode_description = "\\n".join(descriptions)
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
    track_id = "Dima" if "fo2" in file_name else\
               "Yulia" if "yul" in file_name else\
               "George" if "geo" in file_name else\
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

# full list of themes with timings serves as RSS description
# e.g [t + " " + d for (t,d) in zip(timings, descriptions)]
full_title = f"{PODCAST_NAME} #{episode_number}. {episode_comment}"
with open(join(episode_folder, POST_SOCIAL_FILE_NAME), "w") as social_description_file:
    social_description_file.write(f"DATE: {recording_date}\n\n")
    social_description_file.write("PUBLISHING TITLE:\n\n")
    social_description_file.write(full_title + "\n\n")
    social_description_file.write("PUBLISHING CONTENT:\n\n")
    social_description_file.writelines([f"{t} - {d}\n\n" for (t,d) in zip(timings, descriptions)])
    social_description_file.writelines(
        "Мы в социальных сетях: [vk.com/tkittens](https://vk.com/tkittens) | [facebook.com/TKittens](https://www.facebook.com/TKittens) | [t.me/tkittens](https://t.me/tkittens)\n\n")
    social_description_file.writelines([" ".join(link_line)+"\n" for link_line in links])
    social_description_file.write("\n\nPOST CONTENT:\n")
    social_description_file.write(full_title + ".\n\n")
    social_description_file.writelines([f"— {d}\n" for d in descriptions])
    social_description_file.write("\nСсылки на новости на странице подкаста: ")
    social_description_file.write("\nМы на Яндекс.Музыке: https://music.yandex.ru/album/12017408\n")

os.system("open 'https://auphonic.com/engine/'")