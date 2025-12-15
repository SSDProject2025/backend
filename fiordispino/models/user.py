from django.contrib.auth.models import AbstractUser
from django.db import models
from fiordispino.managers import CustomUserManager
from django.contrib.auth.validators import ASCIIUsernameValidator

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email')

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        validators=[ASCIIUsernameValidator()],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        app_label = 'fiordispino'