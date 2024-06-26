from datetime import date
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from rest_framework import status

from core import models


def create_user(username="example",
                email="test@example.com",
                password="example123",
                name="John Doe"):
    return get_user_model().objects.create_user(
        username, email, password, name=name
    )


def create_superuser(username="super",
                     email="super@example.com",
                     password="example123",
                     name="John Doe"):
    return get_user_model().objects.create_superuser(
        username, email, password, name=name
    )


def create_game(title="Example title",
                developer="Example developer",
                duration=50,
                release_date=date(2020, 1, 1),
                in_early_access=False,
                has_multiplayer=False):
    return models.Game.objects.create(
        title=title,
        developer=developer,
        duration=duration,
        release_date=release_date,
        in_early_access=in_early_access,
        has_multiplayer=has_multiplayer
    )


class ModelTests(TestCase):
    def test_create_user(self):
        user = create_user()
        self.assertEqual(user.username, "example")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.name, "John Doe")
        self.assertNotEqual(user.password, "example123")
        self.assertTrue(user.check_password("example123"))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_create_user_with_duplicate_email(self):
        create_user("example", "duplicate@example.com")
        with self.assertRaises(IntegrityError):
            create_user("different", "duplicate@example.com")

    def test_create_user_with_duplicate_username(self):
        create_user("duplicate", "test@example.com")
        with self.assertRaises(IntegrityError):
            create_user("duplicate", "different@example.com")

    def test_create_user_without_needed_credentials(self):
        with self.assertRaises(ValueError):
            create_user("")
        with self.assertRaises(ValueError):
            create_user("example", "")

    def test_create_superuser(self):
        user = create_superuser()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_game_successful(self):
        game = models.Game.objects.create(
            title="Example game title",
            developer="Example developer",
            duration=40,
            release_date=date(2000, 1, 1),
            in_early_access=False,
            has_multiplayer=False
        )
        self.assertEqual(str(game), game.title)
        self.assertEqual(game.developer, "Example developer")
        self.assertEqual(game.duration, 40)
        self.assertEqual(game.release_date, date(2000, 1, 1))
        self.assertFalse(game.in_early_access)
        self.assertFalse(game.has_multiplayer)

    def test_create_game_request_successful(self):
        user = create_user()
        game_req = models.GameRequest.objects.create(
            user=user,
            title="Example game title",
            developer="Example developer",
            duration=40,
            release_date=date(2000, 1, 1),
            in_early_access=False,
            has_multiplayer=False,
        )
        self.assertEqual(str(game_req),
                         f"{game_req.title} request by {game_req.user}")
        self.assertEqual(game_req.developer, "Example developer")
        self.assertEqual(game_req.duration, 40)
        self.assertEqual(game_req.release_date, date(2000, 1, 1))
        self.assertFalse(game_req.in_early_access)
        self.assertFalse(game_req.has_multiplayer)

    def test_create_review_successful(self):
        review = models.Review.objects.create(
            user=create_user(),
            game=create_game(),
            title="Example review title",
            body="Example review body",
            rating=80,
            hours_played=Decimal(10.5),
            percent_finished=Decimal(58.4),
            played_with_friends=True
        )
        self.assertEqual(str(review), f"{review.title} ({review.rating}/100)")
        self.assertEqual(review.body, "Example review body")
        self.assertEqual(review.hours_played, Decimal(10.5))
        self.assertEqual(review.percent_finished, Decimal(58.4))
        self.assertTrue(review.played_with_friends)


class AdminTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="example123"
        )
        self.client.force_login(self.admin_user)
        self.user = create_user()

    def test_get_users_list(self):
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, self.user.username)
        self.assertContains(res, self.user.email)

    def test_get_user_edit_page(self):
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_user_add_page(self):
        url = reverse("admin:core_user_add")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
