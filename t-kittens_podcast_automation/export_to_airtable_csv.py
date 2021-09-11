#!/usr/bin/python3
# Generates and prints episode data in CSV format to export to airtble
# Only needed to restore airtable episodes table by preserved episode descriptions
from os.path import join
from podcast_utils import *

#region metadata constants
EPISODE_PREFIX = "Выпуск "
#endregion

# Sanity check
assert_tkittens_podcast_folder()

# Locate recordings
# print(f"Creating CSV for Episodes")
# print("N,Title,Date Posted,Hosts,Published URL,Status,Episode on Zencastr")
for episode_number in range(0,11):
    episode_folder = build_episode_folder_name(episode_number)
 
    # Fetch data parts (description, timings, links)
    date = ""
    timings = []
    authors = []
    links = []
    briefs = []
    descriptions = []
    with open(join(episode_folder, DESCRIPTION_FILE_NAME)) as file:
        for line in file:
            if date_match := date_regex.match(line):
                date = date_match[1]
            if timing_match := timings_regex.match(line):
                timings.append(timing_match[1])
                authors.append(timing_match[2].replace("Дима","Dima").replace("Жора","George").replace("Юля","Yulia"))
            if link_match := links_regex.match(line):
                links.append(list(filter(None, link_match[1].split(" "))))
            if brief_match := theme_briefs_regex.match(line):
                briefs.append(brief_match[1])
            if description_match := theme_descriptions_regex.match(line):
                descriptions.append(description_match[1])

    public_link = ""
    with open(join(episode_folder, POST_SOCIAL_FILE_NAME)) as file:
        for line in file:
            if public_link_match := public_link_regex.match(line):
                public_link = public_link_match[1]

    # # Generate episode table record
    # #                  N               ,Title,Date Posted,Hosts,Published URL,Status,Episode on Zencastr 
    # post_record = f"""{episode_number},     ,{date}     ,     ,{public_link},Posted,"""
    # print(post_record)
    # Generate news table record
    for (title, timing, description, episode_links, author) in zip(briefs, timings, descriptions, links, authors):
        #                  Title, Time,    Description,  Links,                Author, Episode
        news_record = f"""{title};{timing};{description};{" ".join(episode_links)};{author};{episode_number}"""
        print(news_record)
