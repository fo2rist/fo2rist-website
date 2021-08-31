#!/usr/bin/python3

from datetime import date, timedelta
import os
from podcast_utils import *

# Sanity check
assert_tkittens_podcast_folder()

# Check if the last one exist to not create a new episode every time script is called
last_episode_number = get_last_episode_number()
last_episode_folder = build_episode_folder_name(last_episode_number)

if not is_last_episode_recorded():
    print(f"'{last_episode_folder}' folder doesn't have any audio, must be a new episode already")
    exit(0)

# Create a folder for new episode
new_episode_number = last_episode_number + 1
new_episode_folder = build_episode_folder_name(new_episode_number)
os.makedirs(new_episode_folder, exist_ok=False)
# Put description from template to that folder
full_description_file_name = new_episode_folder + "/" + DESCRIPTION_FILE_NAME
tomorrow = date.today() + timedelta(days=1)
with open(DESCRIPTION_TEMPLATE_FILE_NAME, "r") as template_file:
    with open(full_description_file_name, "w") as description_file:
        for line in template_file:
            description_file.write(
                line.replace("$EPISODE_N", str(new_episode_number))
                    .replace("$RECORDING_INTRO_DATE", tomorrow.strftime("%d %b %Y"))
                    .replace("$RECORDING_DATE", tomorrow.strftime("%Y-%m-%d"))
            )

print(f"'{new_episode_folder}' created")

os.system(f"open '{full_description_file_name}'")
