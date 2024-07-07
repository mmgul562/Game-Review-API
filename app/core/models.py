from decimal import Decimal
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin)

from app import settings


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

    def create_superuser(self, username, email, password, **kwargs):
        user = self.validate_and_create(username, email, password, **kwargs)
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


class Game(models.Model):
    title = models.CharField(max_length=255)
    developer = models.CharField(max_length=255)
    duration = models.PositiveSmallIntegerField(
        null=True,
        help_text="Average number of hours taken to finish the game."
    )
    release_date = models.DateField(null=True)
    in_early_access = models.BooleanField(default=False)
    has_multiplayer = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class GameRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    developer = models.CharField(max_length=255)
    duration = models.PositiveSmallIntegerField(
        null=True,
        help_text="Average number of hours taken to finish the game."
    )
    release_date = models.DateField(null=True)
    in_early_access = models.BooleanField(default=False)
    has_multiplayer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    rejected = models.BooleanField(
        default=False,
        help_text="Current status of the request."
    )
    rejections = models.PositiveSmallIntegerField(
        default=0,
        help_text="Number of rejections."
    )
    # only used when request was rejected
    rejected_at = models.DateTimeField(
        null=True,
        help_text="Date of the last rejection."
    )
    feedback = models.TextField(
        max_length=1023,
        null=True,
        blank=True,
        help_text="Feedback regarding the reason(s) of last rejection."
    )

    def __str__(self):
        return f"{self.title} request by {self.user}"


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    rating = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(100)]
    )
    hours_played = models.DecimalField(
        default=Decimal(1.0),
        max_digits=6,           # max 99 999.9
        decimal_places=1,
        validators=[MinValueValidator(Decimal(0.0))]
    )
    percent_finished = models.DecimalField(
        null=True,
        max_digits=4,
        decimal_places=1,
        validators=[
            MaxValueValidator(Decimal(100.0)),
            MinValueValidator(Decimal(0.0))
        ])
    # true/false for games with multiplayer, otherwise null
    played_with_friends = models.BooleanField(null=True)

    def __str__(self):
        return f"{self.title} ({self.rating}/100)"
