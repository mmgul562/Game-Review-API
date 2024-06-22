from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.tests import create_user


CREATE_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


class PublicUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user_successful(self):
        payload = {
            "username": "example",
            "email": "test@example.com",
            "password": "example123",
            "name": "John Doe"
        }
        res = self.client.post(CREATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(username=payload["username"])
        self.assertNotEqual(user.password, payload["password"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_create_user_with_existing_username(self):
        payload = {
            "username": "example",
            "email": "unique@example.com",
            "password": "example123",
        }
        create_user(username=payload["username"])
        res = self.client.post(CREATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_existing_email(self):
        payload = {
            "username": "unique",
            "email": "test@example.com",
            "password": "example123",
        }
        create_user(email=payload["email"])
        res = self.client.post(CREATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_invalid_password(self):
        payload = {
            "username": "example",
            "email": "test@example.com",
            "password": "1234",
            "name": "John Doe"
        }
        res = self.client.post(CREATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        exists = get_user_model().objects.filter(
            username=payload["username"]
        ).exists()
        self.assertFalse(exists)

    def test_create_token_with_email(self):
        payload = {
            "identifier": "test@example.com",
            "password": "example123"
        }
        create_user(email=payload["identifier"], password=payload["password"])
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("token", res.data)

    def test_create_token_with_username(self):
        payload = {
            "identifier": "example",
            "password": "example123"
        }
        create_user(username=payload["identifier"], password=payload["password"])
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("token", res.data)

    def test_create_token_with_incorrect_password(self):
        payload = {
            "username": "example",
            "password": "incorrect"
        }
        create_user(username=payload["username"])
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_create_token_with_blank_password(self):
        payload = {
            "username": "example",
            "password": ""
        }
        create_user(username=payload["username"])
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_get_user_profile_while_unauthorized(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_user_profile_while_authorized(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            "username": self.user.username,
            "email": self.user.email,
            "name": self.user.name
        })

    def test_update_user(self):
        payload = {
            "email": "updated@example.com",
            "name": "Mary Sue"
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, payload["email"])
        self.assertEqual(self.user.name, payload["name"])

    def test_update_user_all(self):
        payload = {
            "username": "updated",
            "email": "updated@example.com",
            "password": "updated123",
            "name": ""
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.username, payload["username"])
        self.assertEqual(self.user.email, payload["email"])
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))

    def test_update_user_with_invalid_password(self):
        payload = {
            "username": "updated",
            "email": "updated@example.com",
            "password": "1234",
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(self.user.username, payload["username"])
        self.assertNotEqual(self.user.email, payload["email"])
        self.assertFalse(self.user.check_password(payload["password"]))

    def test_update_user_with_existing_username(self):
        existing_user = create_user(
            username="unique",
            email="unique@example.com",
            password="unique123",
            name="John Doe"
        )
        payload = {
            "username": "unique",
            "email": "updated@example.com",
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(self.user.username, existing_user.username)
        self.assertNotEqual(self.user.username, payload["username"])
        self.assertNotEqual(self.user.email, payload["email"])

    def test_update_user_with_existing_email(self):
        existing_user = create_user(
            username="unique",
            email="unique@example.com",
            password="unique123",
        )
        payload = {
            "username": "updated",
            "email": "unique@example.com",
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(self.user.username, payload["username"])
        self.assertNotEqual(self.user.email, existing_user.email)
        self.assertNotEqual(self.user.email, payload["email"])
