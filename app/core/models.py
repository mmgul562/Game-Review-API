from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin)


class UserManager(BaseUserManager):
    def validate_and_create(self, username, email, password, **kwargs):
        if not email or not username:
            raise ValueError('Email and username must be provided.')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **kwargs
        )
        user.set_password(password)
        return user

    def create_user(self, username, email, password=None, **kwargs):
        user = self.validate_and_create(username, email, password, **kwargs)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.validate_and_create(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=64, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'username'
