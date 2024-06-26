from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal

from core.models import Review, Game
from core.tests import create_user, create_game, create_superuser
from review.serializers import ReviewListSerializer, ReviewSerializer


REVIEWS_URL = reverse("review:review-list")


def review_url(review_id):
    return reverse("review:review-detail", args=[review_id])


def create_review(user, game, title="Example title",
                  body="Example review body", rating=80,
                  hours_played=Decimal(20.0), percent_finished=Decimal(90.0),
                  played_with_friends=False):
    return Review.objects.create(
        user=user, game=game, title=title, body=body,
        rating=rating, hours_played=hours_played,
        percent_finished=percent_finished,
        played_with_friends=played_with_friends
    )


def get_game(game_id):
    return Game.objects.get(id=game_id)


def exists(review_id=None, title=None):
    if title:
        return Review.objects.filter(title=title).exists()
    elif review_id:
        return Review.objects.filter(id=review_id).exists()
    return False


class PublicReviewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.game = create_game()

    def test_get_reviews_list(self):
        create_review(user=self.user, game=self.game, title="Review 1")
        create_review(user=self.user, game=self.game, title="Review 2")
        reviews = Review.objects.all().order_by("-id")
        serialized_reviews = ReviewListSerializer(reviews, many=True)
        res = self.client.get(REVIEWS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_reviews.data)

    def test_get_detailed_review(self):
        review = create_review(user=self.user, game=self.game)
        serialized_review = ReviewSerializer(review)
        res = self.client.get(review_url(review.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_review.data)

    def test_create_review_unsuccessful(self):
        payload = {
            "user": self.user,
            "game": self.game.id,
            "title": "Created review title",
            "body": "Created review body",
            "rating": 80,
            "hours_played": Decimal(40.0),
            "percent_finished": Decimal(68.0),
            "played_with_friends": False
        }
        res = self.client.post(REVIEWS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(exists(title=payload["title"]))

    def test_update_review_unsuccessful(self):
        review = create_review(user=self.user, game=self.game)
        updated_game = create_game(title="Updated")
        payload = {
            "title": "Updated title",
            "game": updated_game.id,
            "body": "Updated body",
            "rating": 100,
            "hours_played": Decimal(100.0),
            "percent_finished": Decimal(100.0),
            "played_with_friends": True
        }
        res = self.client.put(review_url(review.id), payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        review.refresh_from_db()
        for key, val in payload.items():
            if key == "game":
                self.assertNotEqual(
                    review.game,
                    get_game(payload["game"])
                )
                continue
            self.assertNotEqual(getattr(review, key), val)

    def test_partial_update_review_unsuccessful(self):
        review = create_review(user=self.user, game=self.game)
        payload = {"rating": 60}
        res = self.client.patch(review_url(review.id), payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        review.refresh_from_db()
        self.assertNotEqual(review.rating, payload["rating"])

    def test_delete_review_unsuccessful(self):
        review = create_review(user=self.user, game=self.game)
        res = self.client.delete(review_url(review.id))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(exists(review_id=review.id))


class PrivateReviewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.game = create_game()
        self.client.force_authenticate(self.user)

    def test_create_review(self):
        payload = {
            "user": self.user,
            "game": self.game.id,
            "title": "Review title",
            "body": "Review body",
            "rating": 80,
            "hours_played": Decimal(40.0),
            "percent_finished": Decimal(68.0),
            "played_with_friends": True
        }
        res = self.client.post(REVIEWS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        review = Review.objects.get(id=res.data["id"])
        self.assertEqual(self.user, review.user)
        for key, val in payload.items():
            if key == "game":
                self.assertEqual(review.game, get_game(payload["game"]))
                continue
            self.assertEqual(getattr(review, key), val)

    def test_update_review(self):
        review = create_review(user=self.user, game=self.game)
        updated_game = create_game(title="Updated")
        payload = {
            "game": updated_game.id,
            "title": "Updated title",
            "body": "Updated body",
            "rating": 100,
            "hours_played": Decimal(100.0),
            "percent_finished": Decimal(100.0),
            "played_with_friends": True
        }
        res = self.client.put(review_url(review.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.user, self.user)
        for key, val in payload.items():
            if key == "game":
                self.assertEqual(review.game, get_game(payload["game"]))
                continue
            self.assertEqual(getattr(review, key), val)

    def test_partial_update_review(self):
        review = create_review(user=self.user, game=self.game)
        payload = {"rating": 60}
        res = self.client.patch(review_url(review.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.rating, payload["rating"])
        self.assertEqual(review.user, self.user)

    def test_update_review_with_too_high_rating(self):
        review = create_review(user=self.user, game=self.game)
        payload = {"rating": 101}
        res = self.client.patch(review_url(review.id), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(review.rating, payload["rating"])

    def test_update_review_with_negative_rating(self):
        review = create_review(user=self.user, game=self.game)
        payload = {"rating": -1}
        res = self.client.patch(review_url(review.id), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(review.rating, payload["rating"])

    def test_update_review_with_negative_hours(self):
        review = create_review(user=self.user, game=self.game)
        payload = {"hours_played": -1}
        res = self.client.patch(review_url(review.id), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(review.hours_played, payload["hours_played"])

    def test_update_review_with_too_high_percentage(self):
        review = create_review(user=self.user, game=self.game)
        payload = {"percent_finished": 101}
        res = self.client.patch(review_url(review.id), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(review.percent_finished,
                            payload["percent_finished"])

    def test_update_review_with_negative_percentage(self):
        review = create_review(user=self.user, game=self.game)
        payload = {"percent_finished": -1}
        res = self.client.patch(review_url(review.id), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(review.percent_finished,
                            payload["percent_finished"])

    def test_delete_review_as_creator(self):
        review = create_review(user=self.user, game=self.game)
        res = self.client.delete(review_url(review.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(exists(review_id=review.id))

    def test_delete_review_as_superuser(self):
        review = create_review(user=self.user, game=self.game)
        self.client.logout()
        superuser = create_superuser()
        self.client.force_authenticate(superuser)
        res = self.client.delete(review_url(review.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(exists(review_id=review.id))

    def test_update_user_unsuccessful(self):
        review = create_review(user=self.user, game=self.game)
        updated_user = create_user(username="updated",
                                   email="updated@example.com")
        payload = {"user": updated_user.id}
        self.client.patch(review_url(review.id), payload)

        review.refresh_from_db()
        self.assertEqual(review.user, self.user)
