from django.urls import reverse
from rest_framework import status

from fiordispino.tests.utils_testing import *


@pytest.mark.django_db
class TestGenreUrl:

    def test_genre_user_can_see(self):
        path = reverse('genre-list')
        client = get_client()
        response = client.get(path)
        assert response.status_code == status.HTTP_200_OK
        obj = parse(response)
        assert obj is not None

    def test_genre_user_can_see_specific_genre(self, genres):
        path = reverse('genre-detail', kwargs={'pk': genres[0].id})
        client = get_client()
        response = client.get(path)
        assert response.status_code == status.HTTP_200_OK
        obj = parse(response)
        assert obj is not None

    def test_genre_non_admin_cant_add(self, game_data, user):
        path = reverse('genre-list')
        client = get_client(user=user)
        response = client.post(path, game_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_genre_non_admin_cant_delete(self, genres, user):
        path = reverse('genre-detail', kwargs={'pk': genres[0].id})
        user = get_client(user=user)
        response = user.delete(path)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_genre_non_admin_cant_update(self, genres, genre_data, user):
        path = reverse('genre-detail', kwargs={'pk': genres[0].id})
        user = get_client(user=user)
        response = user.put(path, genre_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_see(self, admin_user):
        path = reverse('genre-list')
        admin = get_admin(admin_user)
        response = admin.get(path)
        assert response.status_code == status.HTTP_200_OK
        obj = parse(response)
        assert obj is not None

    def test_admin_can_see_specific_genre(self, genres, admin_user):
        path = reverse('genre-detail', kwargs={'pk': genres[0].id})
        admin = get_admin(admin_user)
        response = admin.get(path)
        assert response.status_code == status.HTTP_200_OK
        obj = parse(response)
        assert obj is not None

    def test_admin_can_add(self, admin_user, genre_data):
        path = reverse('genre-list')
        client = get_admin(admin_user)
        response = client.post(path, genre_data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_admin_can_delete(self, admin_user, genres):
        path = reverse('genre-detail', kwargs={'pk': genres[0].id})
        admin = get_admin(admin_user)
        response = admin.delete(path)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_admin_can_update(self, admin_user, genres, genre_data):
        path = reverse('genre-detail', kwargs={'pk': genres[0].id})
        admin = get_admin(admin_user)
        response = admin.put(path, genre_data)
        assert response.status_code == status.HTTP_200_OK