import json
from io import BytesIO

import pytest
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
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
def games_to_play(db, games):
    return [
        mixer.blend('fiordispino.GamesToPlay', game=games[0]),
        mixer.blend('fiordispino.GamesToPlay', game=games[1]),
        mixer.blend('fiordispino.GamesToPlay', game=games[2]),
    ]

@pytest.fixture
def genre(db):
    return mixer.blend('fiordispino.Genre')

@pytest.fixture
def genre_data(db):
    return {'name': 'genre'}

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
def games_to_play_data(db, games):
    return {
        'game': games[0].pk
    }

@pytest.fixture
def admin_user():
    return mixer.blend(get_user_model(), is_staff=True, is_superuser=True)

@pytest.fixture
def user():
    return mixer.blend(get_user_model(), is_staff=False, is_superuser=False)

def get_admin(admin_user):
    res = APIClient()
    #res.force_login(admin_user)
    res.force_authenticate(admin_user)
    return res

def get_client(user=None):
    res = APIClient()
    res.force_authenticate(user=user)
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