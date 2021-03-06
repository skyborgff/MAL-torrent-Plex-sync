import json
import jsonpickle
from json import JSONEncoder

class AnimeInfo:
    def __init__(self, info: dict):
        self.id: str = info.get("@id", None)
        self.restricted: str = info.get("@restricted", None)
        self.type: str = info.get("type", None)
        self.episodecount: str = info.get("episodecount", None)
        self.startdate: str = info.get("startdate", None)
        self.enddate: str = info.get("enddate", None)
        self.titles: Titles = Titles(info.get("titles", None))
        self.relatedanime: Related = Related(info.get("relatedanime", None))
        self.url: str = info.get("url", None)
        self.creators: Creators = Creators(info.get("creators", None))
        self.description: str = info.get("description", "Description Not Available")
        self.ratings: Rating = Rating(info.get("ratings", None))
        self.picture: str = info.get("picture", None)
        self.resources: Resources = Resources(info.get("resources", None))
        self.tags: Tags = Tags(info.get("tags", None))
        self.characters: Characters = Characters(info.get("characters", None))
        self.episodes: Episodes = Episodes(info.get("episodes", None))

    def mal_ids(self):
        return self.resources.from_type(2)


class Titles:
    def __init__(self, titles):
        self.list = []
        if type(titles) is dict:
            try:
                titles = titles["title"]
            except KeyError:
                titles =[titles]
        for title in titles:
            self.list.append(Title(title))

    def main(self) -> str:
        # There should just be one main
        return next((title.text for title in self.list if title.type == "main"), None)

    def official(self) -> str:
        # Todo: Clean up a bit
        # There may be more than one official title
        priority = ["en", "ja"]
        matches = (title for title in self.list if title.type == "official")
        for language in priority:
            title = next((title.text for title in matches if title.language == language), None)
            if title is not None:
                return title
        title = next(iter(matches), None)
        if title is not None:
            return title.text
        else:
            return None


class Title:
    def __init__(self, title_dict: dict):
        self.language = title_dict["@xml:lang"]
        # main, synonym, short, official for seasons, but not for episodes
        self.type = title_dict.get("@type", None)
        self.text = title_dict["#text"]


class Related:
    def __init__(self, related_dict: dict):
        self.list = []
        if related_dict is not None:
            related_list = related_dict["anime"]
            for related in related_list:
                self.list.append(RelatedLinks(related))


class RelatedLinks:
    def __init__(self, related: dict):
        self.id = related["@id"]
        # Sequel, Prequel, Summary
        self.type = related["@type"]
        self.text = related["#text"]


class Creators:
    def __init__(self, creators_dict: dict):
        self.list = []
        if creators_dict is not None:
            creators_list = creators_dict["name"]
            for creator in creators_list:
                self.list.append(Creator(creator))


class Creator:
    def __init__(self, creator_dict: dict):
        self.id = creator_dict["@id"]
        self.type = creator_dict["@type"]
        self.name = creator_dict["#text"]


class Rating:
    def __init__(self, rating_dict: dict):
        self.count = 0
        self.value = 0
        if rating_dict is not None:
            try:
                self.count = rating_dict["permanent"]["@NodeLinksCount"]
                self.value = rating_dict["permanent"]["#text"]
            except KeyError:
                self.count = rating_dict["@votes"]
                self.value = rating_dict["#text"]


class Resources:
    def __init__(self, resources_dict: dict):
        self.list = []
        if resources_dict is not None:
            resources_list = resources_dict["resource"]
            if type(resources_list) is not list:
                resources_list = [resources_list]
            for resource in resources_list:
                self.list.append(Resource(resource))

    def from_type(self, rtype: int) -> list:
        for resource in self.list:
            if resource.type == rtype:
                externalentity = resource.externalentity
                if type(externalentity) is dict:
                    externalentity = [externalentity]
                return externalentity


class Resource:
    # Todo: handle each type differently?
    def __init__(self, resource_dict: dict):
        '''
        Known Types:
        1  : Anime News Network ID
        2  : MAL ID (may be a list check aid #9541, such case, assume lowest?)
        3  :
        4  : Official Website
        5  : Funimation
        6  : Wikipedia EN
        7  : Wikipedia JA
        8  : https://cal.syoboi.jp/ ID
        9  : allcinema ID
        10 : http://anison.info/
        11 : http://lain.gr.jp/
        23 : Twitter
        28 : Crunchyroll
        31 :
        32 : Amazon prime video
        '''
        self.type = resource_dict["@type"]
        self.externalentity = resource_dict["externalentity"]


class Tags:
    def __init__(self, tag_dict: dict):
        self.list = []
        self.name_list = []
        if tag_dict is not None:
            tags_list = tag_dict["tag"]
            for tag in tags_list:
                self.list.append(Tag(tag))
            self.list.sort(key=lambda x: x.weight)
            self.name_list = [tag.name for tag in self.list]


class Tag:
    def __init__(self, tag_dict):
        self.id = tag_dict["@id"]
        self.parentid = tag_dict.get("@parentid", None)
        self.infobox = tag_dict.get("@infobox", None)
        self.weight = tag_dict["@weight"]
        self.localspoiler = tag_dict["@localspoiler"]
        self.globalspoiler = tag_dict["@globalspoiler"]
        self.verified = tag_dict["@verified"]
        self.update = tag_dict["@update"]
        self.name = tag_dict["name"]
        self.picurl = tag_dict.get("description", None)
        self.picurl = tag_dict.get("picurl", None)

class Characters:
    def __init__(self, characters_dict: dict):
        self.list = []
        if characters_dict is not None:
            characters_list = characters_dict["character"]
            for character in characters_list:
                self.list.append(Character(character))


class Character:
    def __init__(self, character_dict):
        self.id = character_dict["@id"]
        self.type = character_dict["@type"]
        self.update = character_dict["@update"]
        self.rating = Rating(character_dict.get("rating", None))
        self.name = character_dict["name"]
        self.gender = character_dict["gender"]
        self.charactertype = CharacterType(character_dict["charactertype"])
        self.description = character_dict.get("description", None)
        self.picture = character_dict["picture"]
        self.seiyuu = Seyuus(character_dict.get("seiyuu", None))


class CharacterType:
    def __init__(self, type_dict: dict):
        self.id = type_dict["@id"]
        self.text = type_dict["#text"]


class Seyuus:
    def __init__(self, seiyuus):
        self.list = []
        if seiyuus is not None:
            if type(seiyuus) is dict:
                seiyuus = [seiyuus]
            for seiyuu in seiyuus:
                self.list.append(Seyuu(seiyuu))


class Seyuu:
    def __init__(self, seiyuu):
        self.id = seiyuu["@id"]
        self.picture = seiyuu["@picture"]
        self.name = seiyuu["#text"]


class Episodes:
    def __init__(self, episodes_dict: dict):
        self.list = []
        if episodes_dict is not None:
            episodes_list = episodes_dict["episode"]
            for episode in episodes_list:
                self.list.append(Episode(episode))


class Episode:
    def __init__(self, episode_dict):
        self.id = episode_dict["@id"]
        self.update = episode_dict["@update"]
        self.type = episode_dict["epno"]["@type"]
        self.number = episode_dict["epno"]["#text"]
        self.length = episode_dict["length"]
        self.airdate = episode_dict.get("airdate", None)
        self.rating = Rating(episode_dict["rating"])
        self.title = Titles(episode_dict["title"])
        self.summary = episode_dict.get("summary", None)
        self.resources = Resources(episode_dict.get("resources", None))


