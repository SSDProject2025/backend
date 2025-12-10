import json
from io import BytesIO

import pytest
from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.defaultfilters import title
from mixer.backend.django import mixer
from rest_framework.test import APIClient


@pytest.fixture
def games(db):
    return [
        mixer.blend('fiordispino.Game', title='Dragon Quest V'),
        mixer.blend('fiordispino.Game', title='Cybperunk'),
        mixer.blend('fiordispino.Game', title='GTA VI'),
    ]


@pytest.fixture
def genres(db):
    return [
        mixer.blend('fiordispino.Genre'),
        mixer.blend('fiordispino.Genre'),
        mixer.blend('fiordispino.Genre'),
    ]

@pytest.fixture
def genre(db):
    return mixer.blend('fiordispino.Genre')

@pytest.fixture
def genre_data(db):
    return {'name': 'genre'}

@pytest.fixture
def games_to_play(db):
    return mixer.blend('fiordispino.GamesToPlay')

@pytest.fixture
def game_data(db, genre):
    file_obj = BytesIO()
    image = Image.new("RGB", (100, 100), (255, 0, 0))
    image.save(file_obj, format='JPEG')
    file_obj.seek(0)

    image_file = SimpleUploadedFile(
        name='test_image.jpg',
        content=file_obj.read(),
        content_type='image/jpeg'
    )

    data = {
        'title': 'Dragon Quest V',
        'description': 'A classic',
        'pegi': 12,
        'release_date': '2011-09-22',
        'genres': [genre.pk],
        'box_art': image_file
    }
    
    return data

@pytest.fixture
def admin_user():
    return mixer.blend(User, is_staff=True, is_superuser=True)


def get_admin(admin_user):
    res = APIClient()
    res.force_login(admin_user)
    return res

def get_client(user=None):
    res = APIClient()
    if user is not None:
        res.force_login(user)
    return res

def parse(response):
    response.render()
    content = response.content.decode()
    return json.loads(content)

def contains(response, key, value):
    obj = parse(response)
    if key not in obj:
        return False
    return value in obj[key]