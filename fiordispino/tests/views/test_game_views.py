import pytest
from io import BytesIO
from PIL import Image
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory, force_authenticate
from django.core.files.uploadedfile import SimpleUploadedFile
from mixer.backend.django import mixer
from django.contrib.auth import get_user_model

from fiordispino.core.exceptions import InvalidNumberOfGamesException
from fiordispino.views import GameViewSet
from fiordispino.models import Game, Genre
from fiordispino.tests.utils_testing import *


@pytest.mark.django_db
class TestGameView:

    @pytest.fixture
    def admin_user(self):
        return mixer.blend(get_user_model(), is_staff=True, is_superuser=True)

    @pytest.fixture
    def normal_user(self):
        return mixer.blend(get_user_model(), is_staff=False)

    def test_list_games_view(self):
        # Create dummy data -> short titles to respect validators
        mixer.blend(Game, title="Super Mario")
        mixer.blend(Game, title="Zelda")
        mixer.blend(Game, title="Metroid")

        factory = APIRequestFactory()
        request = factory.get('/fake-url/')

        # Map the action to list
        view = GameViewSet.as_view({'get': 'list'})
        response = view(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_create_game_view_as_admin(self, admin_user):
        factory = APIRequestFactory()

        genre = mixer.blend(Genre, name="RPG")

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

        # format='multipart' is mandatory when uploading a file
        request = factory.post('/fake-url/', data, format='multipart')

        force_authenticate(request, user=admin_user)


        view = GameViewSet.as_view({'post': 'create'})
        response = view(request)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Dragon Quest V'
        assert Game.objects.count() == 1


    def test_create_game_view_as_normal_user_fails(self, normal_user):
        factory = APIRequestFactory()


        file_obj = BytesIO()
        image = Image.new("RGB", (1, 1), (255, 255, 255))
        image.save(file_obj, format='JPEG')
        file_obj.seek(0)
        image_file = SimpleUploadedFile('test.jpg', file_obj.read(), 'image/jpeg')
        genre = mixer.blend(Genre)

        data = {
            'title': 'Hacker Game',
            'description': '...',
            'pegi': 18,
            'release_date': '2022-01-01',
            'genres': [genre.pk],
            'box_art': image_file
        }

        request = factory.post('/fake-url/', data, format='multipart')

        force_authenticate(request, user=normal_user)

        view = GameViewSet.as_view({'post': 'create'})
        response = view(request)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_random_games_default_value(self, admin_user, available_games):

        # Verify that if 'n_games' is not provided, it defaults to 5.
        client = get_client(admin_user)
        url = reverse('game-get-random-games')

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = parse(response)
        assert len(data) == 5

    def test_get_random_games_custom_value_success(self, admin_user, available_games):
        client = get_client(admin_user)
        url = reverse('game-get-random-games')

        response = client.get(url, {'n_games': 3})

        assert response.status_code == status.HTTP_200_OK
        data = parse(response)
        assert len(data) == 3

    def test_get_random_games_max_limit_success(self, admin_user, available_games):
        client = get_client(admin_user)
        url = reverse('game-get-random-games')

        response = client.get(url, {'n_games': 20})

        assert response.status_code == status.HTTP_200_OK
        data = parse(response)
        assert len(data) == 20

    @pytest.mark.parametrize("invalid_input", [
        "0",  # Too low (min 1)
        "-5",  # Negative
        "21",  # Too high (max 20)
        "abc",  # Not an integer
        "1.5",  # Float instead of int
        "",  # Empty string (if passed explicitly)
    ])
    def test_get_random_games_validation_errors(self, admin_user, available_games, invalid_input):
        client = get_client(admin_user)
        url = reverse('game-get-random-games')

        response = client.get(url, {'n_games': invalid_input})

        assert response.status_code == status.HTTP_400_BAD_REQUEST