from io import BytesIO

import pytest
from PIL import Image
from rest_framework import status
from rest_framework.test import APIRequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from mixer.backend.django import mixer

from fiordispino.views import GameViewSet
from fiordispino.models import Game, Genre


@pytest.mark.django_db
class TestGameView:

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

    def test_create_game_view(self):
        factory = APIRequestFactory()

        # create mock genre
        genre = mixer.blend(Genre, name="RPG")

        file_obj = BytesIO()
        image = Image.new("RGB", (100, 100), (255, 0, 0))  # red image
        image.save(file_obj, format='JPEG')
        file_obj.seek(0)  # go back to the beginiing of the file

        image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=file_obj.read(),  # needs real bytes
            content_type='image/jpeg'
        )

        data = {
            'title': 'Dragon Quest V',
            'description': 'A classic',
            'pegi': 12,
            'release_date': '2011-09-22',
            'genres': [genre.pk],  # genre id as a list because it's a many-to-many relation
            'box_art': image_file
        }

        # format='multipart' is mandatory when uploading a file
        request = factory.post('/fake-url/', data, format='multipart')

        view = GameViewSet.as_view({'post': 'create'})
        response = view(request)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Dragon Quest V'
        assert Game.objects.count() == 1

        created_game = Game.objects.first()
        assert genre in created_game.genres.all()