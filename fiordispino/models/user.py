from django.contrib.auth.models import AbstractUser
from django.db import models
from fiordispino.managers import CustomUserManager

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email')

    username = models.CharField(
        max_length=150,
        unique=False,
        blank=True,
        null=True
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