import pytest
from django.urls import reverse, resolve
from rest_framework.test import APIClient
from rest_framework import status
from mixer.backend.django import mixer
from fiordispino.models import Game


@pytest.mark.django_db
class TestGameUrl:

