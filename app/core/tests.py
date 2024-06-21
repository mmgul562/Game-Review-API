from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


def create_user(email="test@example.com",
                username="example",
                passwd="example123"):
    return get_user_model().objects.create_user(email, username, passwd)


class ModelTests(TestCase):
    def test_create_user(self):
        user = create_user()
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "example")
        self.assertNotEqual(user.password, "example123")
        self.assertTrue(user.check_password("example123"))

    def test_create_user_with_duplicate_email(self):
        create_user("duplicate@example.com", "example")
        with self.assertRaises(IntegrityError):
            create_user("duplicate@example.com", "different")

    def test_create_user_with_duplicate_username(self):
        create_user("test@example.com", "duplicate")
        with self.assertRaises(IntegrityError):
            create_user("different@example.com", "duplicate")

    def test_create_user_without_needed_credentials(self):
        with self.assertRaises(ValueError):
            create_user("")
        with self.assertRaises(ValueError):
            create_user("test@example.com", "")

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            "test@example.com",
            "superuser",
            "example123"
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class AdminTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            username="admin",
            password="example123"
        )
        self.client.force_login(self.admin_user)
        self.user = create_user()

    def test_get_users_list(self):
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.user.username)
        self.assertContains(res, self.user.email)

    def test_get_user_edit_page(self):
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_get_user_add_page(self):
        url = reverse("admin:core_user_add")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
