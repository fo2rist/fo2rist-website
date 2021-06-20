#!/usr/bin/python3
# contains all common files/folders constant and utilities for episodes production

import os
from os.path import join

#region metadata constants
PODCAST_NAME = "Техно-котики"
#endregion

#region folders config

# prefix of final production folder
EPISODE_FOLDER_PREFIX = "Episode "

# filename: template for episode raw description
DESCRIPTION_TEMPLATE_FILE_NAME = "t-kittens_description_template.txt"
# filename: episode's descritpion with additional information
DESCRIPTION_FILE_NAME = "t-kittens_description.txt"
# filename: processed description for social networks
POST_SOCIAL_FILE_NAME = "t-kittens_social_net_description.md"

# path to zencastr episodes
DRIVE_ZENCASTR_RECORDINGS_FOLDER = "../Zencastr"
# path to auphonic production root
DRIVE_AUPHONIC_FOLDER = "../auphonic"
# path to auphonic production results
DRIVE_AUPHONIC_RESULTS_FOLDER = DRIVE_AUPHONIC_FOLDER + "/auphonic-results"
# prefix of zencaster single episode root folder 
ZENCASTR_EPISODE_PREFIX = "t-kittens-"
# prefix of raw zencastr recordings sub-folder
RECORDING_FOLDER_PREFIX = "recording-"

# prefix and suffix for auphonic produced mixed file
PRODUCTION_FILE_PREFIX = "T-Kittens - Episode"
PRODUCTION_FILE_SUFFIX = ". Voice"

# path to intro file
INTRO_AUDIO_FILE = "_audio_snippets/Intro Mono (William Rosati- Floating Also).mp3"
# path to background music file
BACKGROUND_AUDIO_FILE = "_audio_snippets/Background Ambient 1H (Critter Cruise by Matt Harris).mp3"
#endregion

def assert_tkittens_podcast_folder():
    """Check if the folder is podcast root, exit program otherwise"""
    current_dir = os.getcwd()
    if (not current_dir.endswith("T-kittens")):
        print(f"'{current_dir}' is not a T-kittens root folder")
        exit(0)

def get_last_episode_number():
    """Get number of last episode"""
    # Get all episodes' folders 
    subfolders = os.listdir()
    episodes_subfolders = filter(lambda s: s.startswith(EPISODE_FOLDER_PREFIX), subfolders)
    episode_names = map(lambda s: s.replace(EPISODE_FOLDER_PREFIX, ""), episodes_subfolders)
    # and find last
    episode_numbers = sorted([int(s) for s in episode_names if s.isdigit()])
    return episode_numbers[-1]

def build_episode_folder_name(number):
    """Get name of the episode's folder by number"""
    return EPISODE_FOLDER_PREFIX + str(number)

def build_episode_base_file_name(number):
    """Get base name without extension of files production pipeline will generate"""
    return f"{PRODUCTION_FILE_PREFIX} {number}{PRODUCTION_FILE_SUFFIX}"

def get_last_episode_folder_name():
    """Get name of the last episode's folder"""
    return build_episode_folder_name(get_last_episode_number())

def _is_audio_file_name(name):
    return name.endswith(".mp3") or name.endswith(".m4a") or name.endswith(".wav")

def _contains_audio(folder_name):
    return any(_is_audio_file_name(s) for s in os.listdir(folder_name))

def is_last_episode_recorded():
    """Whether last episode production folder contains audio files"""
    last_episode_folder = get_last_episode_folder_name()
    return _contains_audio(last_episode_folder)

def get_recording_folder_path():
    """Get folder path with raw recording files from zencastr"""
    episode_number = get_last_episode_number()
    recording_root_folder = join(DRIVE_ZENCASTR_RECORDINGS_FOLDER, ZENCASTR_EPISODE_PREFIX + str(episode_number))
    recording_subfolders = os.listdir(recording_root_folder)
    if (len(recording_subfolders) == 0):
        raise FileNotFoundError(f"Recordings folder '{recording_root_folder}' is empty")
    # Get last sub-folder, as Zencaster creates multiple when the recording is aborted and restarted
    last_recording_folder_name = list(filter(lambda s: s.startswith(RECORDING_FOLDER_PREFIX), recording_subfolders))[-1]
    recording_folder = join(recording_root_folder, last_recording_folder_name)
    return recording_folder

def get_recording_file_names():
    """Get non-final files from the last episode's folder"""
    recording_folder = get_recording_folder_path()
    recording_files = list(filter(lambda s: s.endswith(".mp3"), os.listdir(recording_folder)))
    return recording_files

def get_auphonic_result_file_names():
    """Get names of files in pre-production results folder"""
    return list(filter(lambda s: s.startswith(PRODUCTION_FILE_PREFIX), os.listdir(DRIVE_AUPHONIC_RESULTS_FOLDER)))

def get_file_for_production():
    """Get pre-produced file name in the episode folder"""
    last_episode_folder = get_last_episode_folder_name()
    production_audio_files = [s for s in os.listdir(last_episode_folder) if _is_audio_file_name(s) and s.startswith(PRODUCTION_FILE_PREFIX)]
    if not production_audio_files:
        return None
    else:
        return join(last_episode_folder, production_audio_files[0])

def is_last_episode_ready_for_production():
    return get_file_for_production() is not None