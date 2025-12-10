import pytest
from django.urls import reverse, resolve
from rest_framework.test import APIClient
from rest_framework import status
from mixer.backend.django import mixer # mixer is a library used to generate mock data
from fiordispino.models import Genre


@pytest.mark.django_db
class TestGenreUrl:

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def genre(self):
        return mixer.blend(Genre)

    def test_genre_list_url_resolves(self):
        path = reverse('genre-list')

        # assert that the path is resolved correctly in the view
        assert resolve(path).view_name == 'genre-list'

    def test_genre_detail_url_resolves(self, genre):
        path = reverse('genre-detail', kwargs={'pk': genre.pk})
        assert resolve(path).view_name == 'genre-detail'

    def test_get_genre_list(self, client):
        # create dummy data, then verify that the get returns something
        mixer.blend(Genre, name="Action")
        mixer.blend(Genre, name="Adventure")
        mixer.blend(Genre, name="RPG")

        path = reverse('genre-list')
        response = client.get(path)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3

    def test_get_genre_detail(self, client, genre):
        # get a spefic genre via primary key
        path = reverse('genre-detail', kwargs={'pk': genre.pk})
        response = client.get(path)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['name'] == genre.name