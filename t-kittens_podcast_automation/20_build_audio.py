#!/usr/bin/python3

# A command to create long background https://superuser.com/questions/820830/loop-audio-file-to-a-given-length
# A command for mixing https://stackoverflow.com/questions/58771658/how-to-add-outro-background-music-to-another-audio-file-with-ffmpeg
# 
# See https://ffmpeg.org/ffmpeg-filters.html for details
# each line of filter takes input number from comman line, or named from previous line `[input]`
# then it applies transfmations separated by comma each with parameters and output name in square brackets
# at the end metadata is copied from the main file


import os
import subprocess
import shutil
from os.path import join
from podcast_utils import *

# Sanity check
assert_tkittens_podcast_folder()

# Check if we have files for production
last_episode_folder = get_last_episode_folder_name()
if not is_last_episode_ready_for_production():
    if not is_last_episode_recorded():
        print(f"'{last_episode_folder}' doesn't have any audio")
        exit(0)
    pre_production_result_files = get_auphonic_result_file_names()
    if not pre_production_result_files:
        print(f"'{DRIVE_AUPHONIC_RESULTS_FOLDER}' doesn't have any result files")
        exit(0)
    # move them to the working folder if we do
    for file in pre_production_result_files:
        print(f"Moving {join(DRIVE_AUPHONIC_RESULTS_FOLDER, file)} to {join(last_episode_folder, file)}")
        shutil.move(join(DRIVE_AUPHONIC_RESULTS_FOLDER, file), join(last_episode_folder, file))
    # and clean up input files
    recording_files = get_recording_file_names()
    for file in recording_files:
        print(f"Removing {join(DRIVE_AUPHONIC_FOLDER, file)} ")
        os.remove(join(DRIVE_AUPHONIC_FOLDER, file))
    
main_audio_file = get_file_for_production()
print(f"Producing {main_audio_file}")

# Remove pre-production file suffix and set the extension to mp3
# we may have either m4a or mp3 - replace it with `.mp3` if needed
output_file = main_audio_file.replace(PRODUCTION_FILE_SUFFIX, "").replace(".m4a", ".mp3")

# get duration of original file to set right timing for fade out
duration = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', main_audio_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout)

# Add intro and background music with ffmpeg. The filter works as follows:
# - background music starts with delay [of 9000ms]
# - intro slightly silenced [85%]
# - main audio receives padding at the end for background music [5s]
# - main audio mixed with long background trimmed at main audio length, and faded during that padding [after 2s for 3s]
# - resulting audio mixed with intro trimmed at audio length
add_intro_and_bg_command = f"""
    ffmpeg -i '{BACKGROUND_AUDIO_FILE}' -i '{INTRO_AUDIO_FILE}' -i '{main_audio_file}'\
    -filter_complex\
    "[0]volume=2,adelay=9s[bg];\
     [1]volume=0.85[intro];\
     [2]volume=1.0,apad=pad_dur=6[fg];\
     [bg][fg]amix=inputs=2:duration=shortest,afade=t=out:st={duration+3}:d=3[episode];\
     [episode][intro]amix=inputs=2:duration=longest"\
    -b:a 128k -map_metadata 2 '{output_file}'
"""

print(add_intro_and_bg_command)
os.system(add_intro_and_bg_command)

os.system("open 'https://anchor.fm/dashboard/episode/new'")
os.system(f"open '{last_episode_folder}'")
# TODO open description file as well
# TODO run blog post creation or make it a step
