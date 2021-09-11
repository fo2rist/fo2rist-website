#!/usr/bin/python3

import re
from datetime import date
from os.path import join
from podcast_utils import *

#region metadata constants
EPISODE_PREFIX = "#"
#endregion
#region website fonders config
WEBSITE_ROOT_FOLDER = "/Users/WeezLabs/Develop/fo2rist-website/t-kittens_website"
WEBSITE_CONTENT_FOLDER = join(WEBSITE_ROOT_FOLDER, "content/blog/")
WEBSITE_DATA_FOLDER = join(WEBSITE_ROOT_FOLDER, "data/subtitles/")
#endregion 

def build_post_file_name(date, number, extension):
    return f"{date}_episode_{number}.{extension}"

def generate_content_for_blog(from_episode, until_episode):
    for episode_number in range(from_episode, until_episode):
        print(f"Generating post #{episode_number}")
        episode_folder = build_episode_folder_name(episode_number)

        # Fetch data parts (description, timings, links)
        date = ""
        authors = []
        links = []
        briefs = []
        descriptions = []
        with open(join(episode_folder, DESCRIPTION_FILE_NAME)) as file:
            for line in file:
                if date_match := date_regex.match(line):
                    date = date_match[1]
                if timing_match := timings_regex.match(line):
                    authors.append(timing_match[2])
                if link_match := links_regex.match(line):
                    links.append(list(link_match[1].split(" ")))
                if brief_match := theme_briefs_regex.match(line):
                    briefs.append(brief_match[1])
                if description_match := theme_descriptions_regex.match(line):
                    descriptions.append(description_match[1])
        authors = list(map(lambda name: name.replace("Дима", HOST_FULL_DIMA).replace("Жора", HOST_FULL_GEORGE).replace("Юля", HOST_FULL_YULIA), authors))
        authors = list(set(authors)) # remove duplicates
        authors.sort()

        public_link = ""
        with open(join(episode_folder, POST_SOCIAL_FILE_NAME)) as file:
            for line in file:
                if public_link_match := public_link_regex.match(line):
                    public_link = public_link_match[1].replace("/episodes/", "/embed/episodes/")

        generate_content_for_episode(date, episode_number, authors, links, briefs, descriptions, public_link)
        generate_subtitles_for_episode(date, episode_number)
        
    
def generate_content_for_episode(date, episode_number, authors, links, briefs, descriptions, public_link):
    print(" - Creating content")
    # Comment - short list of themes
    episode_comment = (", ".join(list(filter(lambda s: not s.startswith('!!'), briefs)))).replace('"', '＂') # fullsize quote is used to circumvent hugo bug with quotes parsing
    # Title - episode number + themes
    episode_title = f"{EPISODE_PREFIX}{episode_number} | {episode_comment}"
    # Authors - mardown list of authors
    episode_authors = "\n  - ".join(authors)
    # Description - long list of themes
    link_number = 1
    abbreviated_links = []
    for topic_links in links:
        formatted_topic_links = []
        for link in topic_links:
            if  len(link) != 0: 
                formatted_topic_links.append(f"[[{link_number}]({link})]")
                link_number += 1
        abbreviated_links.append(" ".join(formatted_topic_links))
    episode_description = "<br/>\n".join([f"— {d} {l}" for (d,l) in zip(descriptions, abbreviated_links)])

    post_content = f"""
---
title: '{episode_title}'
date: {date}
excerpt: '{episode_comment}'
timeToRead: 0
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
    
    print(" - Creating subtitles")
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
