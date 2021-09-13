#!/usr/local/bin/python3

import os
import re
import shutil
from os.path import join
from auphonic_utils import create_auphonic_production
from podcast_utils import *


#region metadata constants
EPISODE_PREFIX = "Выпуск "
#endregion

def copy_recordings_to(recording_files, target_folder):
    for file_name in recording_files:
        shutil.copyfile(
            join(recording_folder, file_name),
            join(target_folder, file_name))

if __name__ == "__main__":    
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
    #  to final Episode folder (primary storage)
    copy_recordings_to(recording_files, episode_folder)
    #  to Auphonic Google Drive files for production
    copy_recordings_to(recording_files, DRIVE_AUPHONIC_FOLDER)

    # Fetch data parts (description, timings, links)
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

    # Validate the metadata
    if len(timings) != len(links)\
            or len(timings) != len(briefs)\
            or len(timings) != len(descriptions):
        print(f"Some metadata is missing!\nFiles {recording_files}\nTimings {timings}\nLinks {links}\nBriefs {briefs}\nDescriptions {descriptions}")
        exit(0)

    # Build common metadata
    briefs_without_ignored = ", ".join(
        list(filter(lambda s: not s.startswith('!!'), briefs)))

    # Generate description for social networks posts
    full_title = f"{PODCAST_NAME} #{episode_number}. {briefs_without_ignored}"
    social_description_path = join(episode_folder, POST_SOCIAL_FILE_NAME)
    if (os.path.exists(social_description_path)):
        print(f"\nSocial description file already exists. Aborting overwrite.")
        exit(0)

    with open(social_description_path, "w") as social_description_file:
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

    create_auphonic_production(
        episode_number = episode_number,
        # Title - prefixed episode number
        episode_title = f"{EPISODE_PREFIX}{episode_number}",
        # Comment - short list of themes, excluding themes starting with '!!'
        episode_comment = briefs_without_ignored,
        # Description - themes of each chapter in the list
        episode_description = "\\n".join(descriptions),
        timings = timings,
        links = links,
        briefs = briefs,
        recording_files = recording_files,
    )

    os.system("open 'https://auphonic.com/engine/'")
