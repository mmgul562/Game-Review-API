from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from rest_framework import status


def create_user(username="example",
                email="test@example.com",
                password="example123",
                name="John Doe"):
    return get_user_model().objects.create_user(
        username, email, password, name=name
    )


def create_superuser(username="example",
                     email="test@example.com",
                     password="example123",
                     name="John Doe"):
    return get_user_model().objects.create_superuser(
        username, email, password, name=name
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
