#!/usr/local/bin/python3

from os.path import exists
from podcast_utils import HOST_DIMA, HOST_GEORGE, HOST_YULIA, date_regex, timings_regex, links_regex, theme_briefs_regex, theme_descriptions_regex, public_link_regex
from airtable_t_kittens_utils import ANCHOR_LINK, AUTHOR, TIMING, get_author_names, get_episode, EPISODE_N, DATE, LINKS, BRIEFS, DESCRIPTIONS, get_news

class Episode:
    """
    Class that describes all data for a single episode of podcast.
    """
    def __init__(self, number: int, recording_date: str, timings = [], authors = [], links = [], briefs = [], descriptions = [], anchor_link: str = None):
        """
        @param recording_date: date in "YYYY-MM-DD" format
        @param timings: list of timings in "MM:SS" format
        @param authors: list of authors in order matching timings
        @param links: list of lists of links in order matching timings, each item may have 0..N links
        @param briefs: list of brief descriptions in order matching timings
        @param descriptions: list of detailed descriptions in order matching timings
        @param anchor_link: link to the episode on anchor.fm
        """
        self.number = number
        self.recording_date = recording_date
        self.__timings = timings
        self.__authors = authors
        self.__links = links
        self.__briefs = briefs
        self.__descriptions = descriptions
        self.anchor_link = anchor_link

    def __get_links_abbreviated_markdown(self):
        link_number = 1
        abbreviated_links = []
        # keep list of links per topic of episode
        for topic_links in self.__links:
            formatted_topic_links = []
            for link in topic_links:
                if  len(link) != 0: 
                    formatted_topic_links.append(f"[[{link_number}]({link})]")
                    link_number += 1
            abbreviated_links.append(" ".join(formatted_topic_links))
        return abbreviated_links

    def __get_anchor_embedable_link(self):
        return self.anchor_link.replace("/episodes/", "/embed/episodes/")

    def __get_unique_authors(self):
        return sorted(set(self.authors))

    def __str__(self):
        """
        Human readable representation of the episode.
        """
        entries = list(zip(self.timings, self.authors, self.briefs, self.descriptions, self.links))
        return f"Episode {self.number} - {self.recording_date}\n{entries}\nPublished: {self.anchor_link}"
    
    #region Dynamic properties
    timings = property(lambda self: self.__timings.copy())
    
    authors = property(lambda self: self.__authors.copy())
    
    links = property(lambda self: self.__links.copy())
    
    briefs = property(lambda self: self.__briefs.copy())
    
    descriptions = property(lambda self: self.__descriptions.copy())
    
    unique_authors = property(__get_unique_authors)
    """List of all authors in alphabetical order."""

    links_markdown = property(__get_links_abbreviated_markdown)
    """Links wrapped in markdown with ordinals at titles."""
    
    anchor_embedable_link = property(__get_anchor_embedable_link)
    #endregion

    #region Public methods
    def is_news_data_complete(self):
        """Check if all news in episode have timings, briefs, description, and (potentially empty) list of links"""
        return len(self.timings) == len(self.links) and\
            len(self.timings) == len(self.briefs) and\
            len(self.timings) == len(self.descriptions)
    #endregion

def read_from_file(episode_number: int, description_path: str, social_post_path: str = None) -> Episode:
    # Fetch data parts (description, timings, links)
    recording_date = ""
    timings = []
    authors = []
    links = []
    briefs = []
    descriptions = []
    with open(description_path) as file:
        for line in file:
            if date_match := date_regex.match(line):
                recording_date = date_match[1]
            if timing_match := timings_regex.match(line):
                timings.append(timing_match[1])
                authors.append(timing_match[2])
            if link_match := links_regex.match(line):
                links.append(list(link_match[1].split(" ")))
            if brief_match := theme_briefs_regex.match(line):
                briefs.append(brief_match[1])
            if description_match := theme_descriptions_regex.match(line):
                descriptions.append(description_match[1])

    x_public_link = None
    if social_post_path and exists(social_post_path):
        with open(social_post_path) as file:
            for line in file:
                if public_link_match := public_link_regex.match(line):
                    x_public_link = public_link_match[1]

    # In description file names are in Russian
    authors_short_names = list(map(lambda name: name.replace("Дима", HOST_DIMA).replace("Жора", HOST_GEORGE).replace("Юля", HOST_YULIA), authors))

    episode = Episode(episode_number, recording_date, timings, authors_short_names, links, briefs, descriptions, x_public_link)
    return episode

def read_from_airtable(episode_number: int) -> Episode:
    """
    Read complete episode data from AirTable.
    @returns None if episode not found 
    """
    try:
        episode_data = get_episode(episode_number)
        episode_number = episode_data[EPISODE_N]
        news = get_news(episode_number)
    except:
        print(f'Episode {episode_number} can not be read from AirTable')
        return None
    # Episodes may not have links, in this case AirTable won't return column at all, so replace with empty list if needed
    links = episode_data.get(LINKS) or []
    
    episode = Episode(
        episode_number,
        episode_data[DATE],
        timings = list(map(lambda item: f"{item[TIMING] // 60}:{item[TIMING] % 60}", news)),
        authors = get_author_names(list(map(lambda item: item[AUTHOR][0], news))),
        links = list(map(lambda links_str: links_str.split(' '), links)),
        briefs = episode_data[BRIEFS],
        descriptions = episode_data[DESCRIPTIONS],
        anchor_link = episode_data[ANCHOR_LINK])
    return episode
