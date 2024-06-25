from datetime import date
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Game
from core.tests import (create_user,
                        create_superuser,
                        create_game)
from game.serializers import GameSerializer


GAMES_URL = reverse("game:game-list")


def game_url(game_id):
    return reverse("game:game-detail", args=[game_id])


def exists(id=None, title=None):
    if id:
        return Game.objects.filter(id=id).exists()
    elif title:
        return Game.objects.filter(title=title).exists()
    return False


class PublicGameApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()

    def test_get_games_list(self):
        create_game(title="Game 1")
        create_game(title="Game 2")
        games = GameSerializer(Game.objects.all(), many=True)
        res = self.client.get(GAMES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, games.data)

    def test_get_detailed_game(self):
        game = create_game()
        serialized_game = GameSerializer(game)
        res = self.client.get(game_url(game.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_game.data)

    def test_add_game(self):
        payload = {
            "title": "Example title",
            "developer": "Example developer",
            "duration": 50,
            "release_date": date(2020, 1, 1),
            "in_early_access": True,
            "has_multiplayer": False
        }
        res = self.client.post(GAMES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(exists(title=payload["title"]))

    def test_update_game(self):
        game = create_game()
        payload = {
            "title": "Updated title",
            "developer": "Updated developer",
            "duration": 90,
            "release_date": date(2013, 6, 10),
            "in_early_access": True,
            "has_multiplayer": True
        }
        res = self.client.put(game_url(game.id), payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        game.refresh_from_db()
        for key, val in payload.items():
            self.assertNotEqual(getattr(game, key), val)

    def test_partial_update_game(self):
        game = create_game()
        payload = {"duration": 60}
        res = self.client.patch(game_url(game.id), payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        game.refresh_from_db()
        self.assertNotEqual(game.duration, payload["duration"])

    def test_delete_game(self):
        game = create_game()
        res = self.client.delete(game_url(game.id))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(exists(id=game.id))


class UserGameApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_add_game(self):
        payload = {
            "title": "Example title",
            "developer": "Example developer",
            "duration": 50,
            "release_date": date(2020, 1, 1),
            "in_early_access": True,
            "has_multiplayer": False
        }
        res = self.client.post(GAMES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(exists(title=payload["title"]))

    def test_update_game(self):
        game = create_game()
        payload = {
            "title": "Updated title",
            "developer": "Updated developer",
            "duration": 90,
            "release_date": date(2010, 2, 2),
            "in_early_access": True,
            "has_multiplayer": True
        }
        res = self.client.put(game_url(game.id), payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        game.refresh_from_db()
        for key, val in payload.items():
            self.assertNotEqual(getattr(game, key), val)

    def test_partial_update_game(self):
        game = create_game()
        payload = {"duration": 60}
        res = self.client.patch(game_url(game.id), payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        game.refresh_from_db()
        self.assertNotEqual(game.duration, payload["duration"])

    def test_delete_game(self):
        game = create_game()
        res = self.client.delete(game_url(game.id))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(exists(id=game.id))


class SuperUserGameApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.superuser = create_superuser()
        self.client.force_authenticate(self.superuser)

    def test_add_game(self):
        payload = {
            "title": "Example title",
            "developer": "Example developer",
            "duration": 50,
            "release_date": date(2020, 1, 1),
            "in_early_access": True,
            "has_multiplayer": False
        }
        res = self.client.post(GAMES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists(title=payload["title"]))

    def test_update_game(self):
        game = create_game()
        payload = {
            "title": "Updated title",
            "developer": "Updated developer",
            "duration": 90,
            "release_date": date(2010, 10, 10),
            "in_early_access": True,
            "has_multiplayer": True
        }
        res = self.client.put(game_url(game.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        game.refresh_from_db()
        for key, val in payload.items():
            self.assertEqual(getattr(game, key), val)

    def test_partial_update_game(self):
        game = create_game()
        payload = {"duration": 60}
        res = self.client.patch(game_url(game.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        game.refresh_from_db()
        self.assertEqual(game.duration, payload["duration"])

    def test_delete_game(self):
        game = create_game()
        res = self.client.delete(game_url(game.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(exists(id=game.id))
