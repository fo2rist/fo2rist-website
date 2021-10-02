#!/usr/local/bin/python3

import re
from os.path import join
from podcast_utils import *
from t_kittens_episode import read_from_airtable

#region website fonders config
WEBSITE_ROOT_FOLDER = "/Users/WeezLabs/Develop/fo2rist-website/t-kittens_website"
WEBSITE_CONTENT_FOLDER = join(WEBSITE_ROOT_FOLDER, "content/blog/")
WEBSITE_DATA_FOLDER = join(WEBSITE_ROOT_FOLDER, "data/subtitles/")
#endregion 

#region metadata constants
EPISODE_PREFIX = "#"
#endregion

def build_post_file_name(date, number, extension):
    return f"{date}_episode_{number}.{extension}"

def generate_content_for_blog(from_episode, until_episode):
    for episode_number in range(from_episode, until_episode):
        print(f"Generating post #{episode_number}")

        print(" - Reading post data")
        episode = read_from_airtable(episode_number)

        # process data parts for blog
        all_authors_full_names = list(map(lambda name: name
                    .replace(HOST_DIMA, HOST_FULL_DIMA)
                    .replace(HOST_GEORGE, HOST_FULL_GEORGE)
                    .replace(HOST_YULIA, HOST_FULL_YULIA), 
                episode.unique_authors))

        print(" - Creating content")
        generate_content_for_episode(episode.recording_date, episode.number, all_authors_full_names, episode.links_markdown, episode.briefs, episode.descriptions, episode.anchor_embedable_link)

        print(" - Creating subtitles")
        generate_subtitles_for_episode(episode.recording_date, episode.number)

def generate_content_for_episode(date, episode_number, authors, links_markdown, briefs, descriptions, public_link):
    # Comment - short list of themes
    episode_comment = (", ".join(list(filter(lambda s: not s.startswith('!!'), briefs)))).replace('"', '＂') # fullsize quote is used to circumvent hugo bug with quotes parsing
    # Title - episode number + themes
    episode_title = f"{EPISODE_PREFIX}{episode_number} | {episode_comment}"
    # Authors - mardown list of authors
    episode_authors = "\n  - ".join(authors)
    # Description - long list of themes + links
    episode_description = "<br/>\n".join([f"— {d} {l}" for (d,l) in zip(descriptions, links_markdown)])
    # Duration of final audio file in seconds
    episode_duration = int(get_audio_duration(get_production_target_file(episode_number)))

    post_content = f"""
---
title: '{episode_title}'
date: {date}
excerpt: '{episode_comment}'
timeToRead: {episode_duration}
authors:
  - {episode_authors}
---

{episode_description}

{{{{< anchor-episode-large "{public_link}" >}}}}
"""
    with open(join(WEBSITE_CONTENT_FOLDER, build_post_file_name(date, episode_number, "md")), "w") as post_file:
        post_file.write(post_content)


def generate_subtitles_for_episode(date, episode_number):
    def sanitize(string):
        # google's voice recognition often makes this type of mistake
        return re.sub(r"наркотик", "Техно-котик", string, flags=re.IGNORECASE)

    episode_folder = build_episode_folder_name(episode_number)
    subtitles_file_file = build_episode_base_file_name(episode_number) + ".json"
    try:
        with open(join(episode_folder, subtitles_file_file)) as source_file:
            with open(join(WEBSITE_DATA_FOLDER, build_post_file_name(date, episode_number, "json")), "w") as target_file:
                for line in source_file:
                    target_file.writelines(sanitize(line))
    except IOError as exc:
        print(f" ! subtitles not created: {exc}")

if __name__ == "__main__":
    # Sanity check
    assert_tkittens_podcast_folder()
    # Locate recordings
    last_episode_number = get_last_episode_number()
    
    generate_content_for_blog(from_episode = last_episode_number, until_episode = last_episode_number + 1)
