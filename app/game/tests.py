from datetime import date
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Game, GameRequest
from core.tests import (create_user,
                        create_superuser,
                        create_game)
from game.serializers import GameSerializer, GameRequestSerializer

GAMES_URL = reverse("game:game-list")
REQ_URL = reverse("game:gamerequest-list")


def game_url(game_id):
    return reverse("game:game-detail", args=[game_id])


def req_url(req_id):
    return reverse("game:gamerequest-detail", args=[req_id])


def create_game_request(user,
                        title="Example title",
                        developer="Example developer",
                        duration=50,
                        release_date=date(2020, 1, 1),
                        in_early_access=False,
                        has_multiplayer=False,
                        rejected=False,
                        rejections=0,
                        rejected_at=None,
                        feedback=None):
    return GameRequest.objects.create(
        user=user,
        title=title,
        developer=developer,
        duration=duration,
        release_date=release_date,
        in_early_access=in_early_access,
        has_multiplayer=has_multiplayer,
        rejected=rejected,
        rejections=rejections,
        rejected_at=rejected_at,
        feedback=feedback
    )


def exists(req=False, id=None, title=None):
    if not req:
        if id:
            return Game.objects.filter(id=id).exists()
        elif title:
            return Game.objects.filter(title=title).exists()
    if id:
        return GameRequest.objects.filter(id=id).exists()
    elif title:
        return GameRequest.objects.filter(title=title).exists()
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


class PublicGameRequestApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()

    def test_get_game_requests_list(self):
        create_game_request(user=self.user)
        create_game_request(user=self.user)
        requests = GameRequest.objects.all()
        serialized_requests = GameRequestSerializer(requests, many=True)
        res = self.client.get(REQ_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(serialized_requests, res.data)

    def test_get_game_request(self):
        request = create_game_request(user=self.user)
        serialized_request = GameRequestSerializer(request)
        res = self.client.get(req_url(request.id))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(serialized_request, res.data)

    def test_create_game_request(self):
        payload = {
            "title": "Example title",
            "developer": "Example developer",
            "duration": 40,
            "release_date": date(2020, 5, 5),
            "in_early_access": False,
            "has_multiplayer": True,
        }
        res = self.client.post(REQ_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(exists(req=True, title=payload["title"]))

    def test_update_game_request(self):
        request = create_game_request(user=self.user)
        payload = {
            "title": "Updated title",
            "developer": "Updated developer",
            "duration": 90,
            "release_date": date(2010, 2, 6),
            "in_early_access": True,
            "has_multiplayer": True,
        }
        res = self.client.put(req_url(request.id), payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        request.refresh_from_db()
        for key, val in payload.items():
            self.assertNotEqual(getattr(request, key), val)

    def test_partial_update_game_request(self):
        request = create_game_request(user=self.user)
        payload = {"developer": "Updated developer"}
        res = self.client.patch(req_url(request.id), payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        request.refresh_from_db()
        self.assertNotEqual(request.developer, payload["developer"])

    def test_delete_game_request(self):
        request = create_game_request(user=self.user)
        res = self.client.delete(req_url(request.id))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(exists(req=True, id=request.id))


class PrivateGameRequestApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_get_game_requests_list(self):
        other_user = create_user(username="diff", email="diff@example.com")
        create_game_request(user=self.user)
        create_game_request(user=self.user)
        create_game_request(user=other_user)
        requests = GameRequest.objects.filter(user=self.user)
        serialized_requests = GameRequestSerializer(requests, many=True)
        res = self.client.get(REQ_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for req, res_req in zip(serialized_requests.data, res.data):
            for key, val in req.items():
                if key in ["feedback", "rejected_at", "rejections"]:
                    continue
                self.assertEqual(res_req[key], val)

    def test_get_game_request(self):
        request = create_game_request(user=self.user)
        serialized_request = GameRequestSerializer(request)
        res = self.client.get(req_url(request.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key, val in serialized_request.data.items():
            if key in ["feedback", "rejected_at", "rejections"]:
                continue
            self.assertEqual(res.data[key], val)

    def test_get_other_users_game_request(self):
        other_user = create_user(username="diff", email="diff@example.com")
        request = create_game_request(user=other_user)
        serialized_request = GameRequestSerializer(request)
        res = self.client.get(req_url(request.id))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(res.data, serialized_request.data)

    def test_create_game_request(self):
        payload = {
            "title": "Example title",
            "developer": "Example developer",
            "duration": 40,
            "release_date": date(2020, 5, 5),
            "in_early_access": False,
            "has_multiplayer": True,
        }
        res = self.client.post(REQ_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists(req=True, title=payload["title"]))

    def test_update_game_request(self):
        request = create_game_request(user=self.user)
        payload = {
            "title": "Updated title",
            "developer": "Updated developer",
            "duration": 90,
            "release_date": date(2010, 2, 6),
            "in_early_access": True,
            "has_multiplayer": True,
        }
        res = self.client.put(req_url(request.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        request.refresh_from_db()
        for key, val in payload.items():
            self.assertEqual(getattr(request, key), val)

    def test_update_rejected_game_request(self):
        request = create_game_request(user=self.user, rejected=True,
                                      rejected_at=timezone.now(), rejections=3)
        payload = {
            "title": "Updated title",
            "developer": "Updated developer",
            "duration": 90,
            "release_date": date(2010, 2, 6),
            "in_early_access": True,
            "has_multiplayer": True,
        }
        res = self.client.put(req_url(request.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        request.refresh_from_db()
        self.assertFalse(request.rejected)
        for key, val in payload.items():
            self.assertEqual(getattr(request, key), val)

    def test_update_rejected_game_request_with_error_400(self):
        request = create_game_request(user=self.user, rejected=True,
                                      rejected_at=timezone.now(), rejections=3)
        payload = {"title": "Updated title"}
        res = self.client.put(req_url(request.id), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        request.refresh_from_db()
        self.assertTrue(request.rejected)

    def test_partial_update_game_request(self):
        request = create_game_request(user=self.user)
        payload = {"developer": "Updated developer"}
        res = self.client.patch(req_url(request.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        request.refresh_from_db()
        self.assertEqual(request.developer, payload["developer"])

    def test_partial_update_rejected_game_request(self):
        request = create_game_request(user=self.user, rejected=True,
                                      rejected_at=timezone.now(), rejections=2)
        payload = {"developer": "Updated developer"}
        res = self.client.patch(req_url(request.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        request.refresh_from_db()
        self.assertFalse(request.rejected)
        self.assertEqual(request.developer, payload["developer"])

    def test_delete_game_request(self):
        request = create_game_request(user=self.user)
        res = self.client.delete(req_url(request.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(exists(req=True, id=request.id))


class SuperUserGameRequestApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.superuser = create_superuser()
        self.user = create_user()
        self.client.force_authenticate(self.superuser)

    def test_get_all_game_requests(self):
        create_game_request(user=self.user)
        other_user = create_user(username="diff", email="diff@example.com")
        create_game_request(user=other_user)
        requests = GameRequest.objects.all()
        serialized_requests = GameRequestSerializer(requests, many=True)
        res = self.client.get(REQ_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_requests.data)

    def test_get_other_users_game_request(self):
        request = create_game_request(user=self.user)
        res = self.client.get(req_url(request.id))
        serialized_request = GameRequestSerializer(request)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_request.data)

    def test_approve_game_request(self):
        request = create_game_request(user=self.user)
        url = f"/api/game/game-requests/{request.id}/approve/"
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists(title=request.title))
        self.assertFalse(exists(req=True, id=request.id))

    def test_reject_game_request(self):
        request = create_game_request(user=self.user)
        url = f"/api/game/game-requests/{request.id}/reject/"
        payload = {"feedback": "Example feedback"}
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(exists(title=request.title))
        request.refresh_from_db()
        self.assertTrue(request.rejected)
        self.assertEqual(request.rejections, 1)
        self.assertIsNotNone(request.rejected_at)
        self.assertEqual(request.feedback, payload["feedback"])

    def test_reject_previously_rejected_game_request(self):
        rejected_at = timezone.now()
        request = create_game_request(user=self.user, rejected=False,
                                      rejections=2, rejected_at=rejected_at)
        url = f"/api/game/game-requests/{request.id}/reject/"
        payload = {"feedback": "Example feedback"}
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        request.refresh_from_db()
        self.assertTrue(request.rejected)
        self.assertNotEqual(request.rejected_at, rejected_at)
        self.assertEqual(request.rejections, 3)

    def test_reject_currently_rejected_game_request(self):
        rejected_at = timezone.now()
        request = create_game_request(user=self.user, rejected=True,
                                      rejections=1, rejected_at=rejected_at)
        url = f"/api/game/game-requests/{request.id}/reject/"
        payload = {"feedback": "Example feedback"}
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        request.refresh_from_db()
        self.assertEqual(request.rejections, 1)
        self.assertEqual(request.rejected_at, rejected_at)
        self.assertNotEqual(request.feedback, payload["feedback"])
