#!/usr/local/bin/python3

import os
import re
import shutil
from os.path import join
from t_kittens_episode import read_from_file
from auphonic_utils import create_auphonic_production
from podcast_utils import *


#region metadata constants
EPISODE_PREFIX = "Выпуск "
#endregion

def copy_recordings_to(recording_files, source_folder, target_folder):
    """Copy files by name from source folder to target folder"""
    
    for file_name in recording_files:
        shutil.copyfile(
            join(source_folder, file_name),
            join(target_folder, file_name))

def generate_social_network_description(
    episode_number,
    recording_date,
    timings,
    links,
    briefs_without_ignored,
    descriptions,
):
    """Create file with templates for social networks"""

    full_title = f"{PODCAST_NAME} #{episode_number}. {briefs_without_ignored}"
    social_post_path = join(episode_folder, POST_SOCIAL_FILE_NAME)
    if (os.path.exists(social_post_path)):
        print(f"Social description file already exists. Aborting overwrite.")
        exit(0)

    with open(social_post_path, "w") as social_post_file:
        social_post_file.write(f"DATE: {recording_date}\n\n")
        social_post_file.write("PUBLISHING TITLE:\n\n")
        social_post_file.write(full_title + "\n\n")
        social_post_file.write("PUBLISHING CONTENT:\n\n")
        social_post_file.writelines([f"{t} - {d}\n\n" for (t,d) in zip(timings, descriptions)])
        social_post_file.writelines(
            "Мы в социальных сетях: [vk.com/tkittens](https://vk.com/tkittens) | [facebook.com/TKittens](https://www.facebook.com/TKittens) | [t.me/tkittens](https://t.me/tkittens)\n\n")
        social_post_file.writelines([" ".join(link_line)+"\n" for link_line in links])
        social_post_file.write("\n\nPOST CONTENT:\n")
        social_post_file.write(full_title + ".\n\n")
        social_post_file.writelines([f"— {d}\n" for d in descriptions])
        social_post_file.write("\nСсылки на новости на странице подкаста: ")
        social_post_file.write("\nМы на Яндекс.Музыке: https://music.yandex.ru/album/12017408\n")

if __name__ == "__main__":    
    # Sanity check
    assert_tkittens_podcast_folder()

    # Locate recordings and data files
    episode_number = get_last_episode_number()
    episode_folder = get_last_episode_folder_name()
    description_path = join(episode_folder, DESCRIPTION_FILE_NAME)

    try:
        recording_folder = get_recording_folder_path()
        recording_files = get_recording_file_names()
    except FileNotFoundError as err:
        print(f"Recording folder for last episode doesn't exist: {err}")
        exit(0)

    # Move single track recording to production folders
    #  to final Episode folder (primary storage)
    copy_recordings_to(recording_files, recording_folder, episode_folder)
    #  to Auphonic Google Drive files for production
    copy_recordings_to(recording_files, recording_folder, DRIVE_AUPHONIC_FOLDER)

    # Read episode data
    episode = read_from_file(episode_number, description_path)
    # and validate it
    if not episode.is_news_data_complete():
        print(f"Some data for production is missing:\n{episode}")
        exit(0)

    # Create content for social networks
    briefs_without_ignored = ", ".join(
        list(filter(lambda s: not s.startswith('!!'), episode.briefs)))
    generate_social_network_description(episode.number, episode.recording_date, episode.timings, episode.links, briefs_without_ignored, episode.descriptions)

    # Initiate audio rendering at Auphonic
    create_auphonic_production(
        episode_number = episode_number,
        # Title - prefixed episode number
        episode_title = f"{EPISODE_PREFIX}{episode_number}",
        # Comment - short list of themes, excluding themes starting with '!!'
        episode_comment = briefs_without_ignored,
        # Description - themes of each chapter in the list
        episode_description = "\\n".join(episode.descriptions),
        timings = episode.timings,
        links = episode.links,
        briefs = episode.briefs,
        recording_files = recording_files,
    )

    os.system("open 'https://auphonic.com/engine/'")
