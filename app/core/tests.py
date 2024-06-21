from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


class ModelTests(TestCase):
    @staticmethod
    def create_user(email="test@example.com",
                    username="example",
                    passwd="example123"):
        return get_user_model().objects.create_user(email, username, passwd)

    def test_create_user_successful(self):
        user = ModelTests.create_user()
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "example")
        self.assertNotEqual(user.password, "example123")
        self.assertTrue(user.check_password("example123"))

    def test_create_user_with_duplicate_email(self):
        ModelTests.create_user("duplicate@example.com", "example")
        with self.assertRaises(IntegrityError):
            ModelTests.create_user("duplicate@example.com", "different")

    def test_create_user_with_duplicate_username(self):
        ModelTests.create_user("test@example.com", "duplicate")
        with self.assertRaises(IntegrityError):
            ModelTests.create_user("different@example.com", "duplicate")

    def test_create_user_without_needed_credentials(self):
        with self.assertRaises(ValueError):
            ModelTests.create_user("")
        with self.assertRaises(ValueError):
            ModelTests.create_user("test@example.com", "")

    def test_create_superuser_successful(self):
        user = get_user_model().objects.create_superuser(
            "test@example.com",
            "superuser",
            "example123"
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
