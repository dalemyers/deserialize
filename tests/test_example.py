"""Test deserializing."""

import os
import sys
from typing import List
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import deserialize

# pylint: enable=wrong-import-position


class Actor:
    """Represents an actor."""

    name: str
    age: int


class Episode:
    """Represents an episode."""

    title: str
    identifier: str
    actors: List[Actor]


class Season:
    """Represents a season."""

    episodes: List[Episode]
    completed: bool


class TVShow:
    """Represents a TV show."""

    seasons: List[Season]
    creator: str


class DeserializationExampleTestSuite(unittest.TestCase):
    """Deserialization example test cases."""

    def test_example(self):
        """Test that the example from the README deserializes correctly."""

        actor_data = [{"name": "Man", "age": 35}, {"name": "Woman", "age": 52}]

        episode_data = [
            {"title": "Some Episode", "identifier": "abcdef", "actors": actor_data}
        ]

        season_data = [{"episodes": episode_data, "completed": True}]

        show_data = {"seasons": season_data, "creator": "Person"}

        show = deserialize.deserialize(TVShow, show_data)
        self.assertEqual(show.creator, show_data["creator"])
        self.assertEqual(len(show.seasons), len(season_data))

        season = show.seasons[0]
        self.assertEqual(season.completed, season_data[0]["completed"])
        self.assertEqual(len(season.episodes), len(season_data[0]["episodes"]))

        episode = season.episodes[0]
        self.assertEqual(episode.title, episode_data[0]["title"])
        self.assertEqual(episode.identifier, episode_data[0]["identifier"])
        self.assertEqual(len(episode.actors), len(episode_data[0]["actors"]))

        actors = episode.actors
        for index, actor in enumerate(actors):
            self.assertEqual(actor.name, actor_data[index]["name"])
            self.assertEqual(actor.age, actor_data[index]["age"])
