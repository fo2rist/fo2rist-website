#!/usr/bin/python3

import re
from datetime import date
from os.path import join
from podcast_utils import *

#region metadata constants
PODCAST_NAME = "Техно-котики"
EPISODE_PREFIX = "Выпуск "
#endregion

# Sanity check
assert_tkittens_podcast_folder()

# Locate recordings
last_episode_number = get_last_episode_number()
for episode_number in range(36, last_episode_number+1):
    print(f"Creating {episode_number}")
    episode_folder = build_episode_folder_name(episode_number)

    # Fetch data parts (description, timings, links)
    date_regex = re.compile(r"DATE: (\d\d\d\d-\d\d?-\d\d?)")
    theme_briefs_regex = re.compile(r"THEME_\d_SHORT:\s*(.*)")
    theme_descriptions_regex = re.compile(r"THEME_\d_FULL:\s*(.*)")
    date = ""
    briefs = []
    descriptions = []
    with open(join(episode_folder, DESCRIPTION_FILE_NAME)) as file:
        for line in file:
            if date_match := date_regex.match(line):
                date = date_match[1]
            if brief_match := theme_briefs_regex.match(line):
                briefs.append(brief_match[1])
            if description_match := theme_descriptions_regex.match(line):
                descriptions.append(description_match[1])

    public_link_regex = re.compile(r".*(https://anchor.fm/t-kittens/episodes.*)")
    public_link = ""
    with open(join(episode_folder, POST_SOCIAL_FILE_NAME)) as file:
        for line in file:
            if public_link_match := public_link_regex.match(line):
                public_link = public_link_match[1].replace("/episodes/", "/embed/episodes/")

    # Title - episode number
    episode_title = f"{PODCAST_NAME} — {EPISODE_PREFIX}{episode_number}"
    # Comment - short list of themes
    episode_comment = ", ".join(briefs)
    # Description - long list of themes
    episode_description = "\n".join([f"— {d}\n" for d in descriptions])

    post_content = f"""
---
title: {episode_title}
date: {date}
hero: /images/t-kittens_w_wide.png
excerpt: {episode_comment}
timeToRead: 0
authors:
  - Dmitry Sitnikov
  - George Ymydykov
  - Yulia Terterian
---

{episode_description}

{{{{< anchor-episode-large "{public_link}" >}}}}
"""

    with open(join("/Users/WeezLabs/Develop/fo2rist-website/t-kittens_website/content/blog/", f"{date}_episode_{episode_number}.md"), "w") as post_file:
        post_file.write(post_content)
