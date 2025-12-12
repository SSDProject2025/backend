from django.urls import reverse
from rest_framework import status

from fiordispino.tests.utils_testing import *


@pytest.mark.django_db
class TestGameUrl:

    # --- USER TESTS (Read Only) ---

    def test_games_user_can_see(self):
        path = reverse('game-list')
        client = get_client()
        response = client.get(path)
        assert response.status_code == status.HTTP_200_OK
        obj = parse(response)
        assert obj is not None

    def test_games_user_can_see_specific_game(self, games):
        path = reverse('game-detail', kwargs={'pk': games[0].id})
        client = get_client()
        response = client.get(path)
        assert response.status_code == status.HTTP_200_OK
        obj = parse(response)
        assert obj is not None

    # --- USER TESTS (Forbidden Actions) ---

    def test_games_non_admin_cant_add(self, game_data):
        path = reverse('game-list')
        client = get_client()

        response = client.post(path, game_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_games_non_admin_cant_delete(self, games):
        path = reverse('game-detail', kwargs={'pk': games[0].id})
        client = get_client()
        response = client.delete(path)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_games_non_admin_cant_update(self, games, game_data):
        path = reverse('game-detail', kwargs={'pk': games[0].id})
        client = get_client()

        response = client.put(path, game_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # --- ADMIN TESTS (Full Access) ---

    def test_admin_can_see(self, admin_user):
        path = reverse('game-list')
        admin = get_admin(admin_user)
        response = admin.get(path)
        assert response.status_code == status.HTTP_200_OK
        obj = parse(response)
        assert obj is not None

    def test_admin_can_see_specific_game(self, games, admin_user):
        path = reverse('game-detail', kwargs={'pk': games[0].id})
        admin = get_admin(admin_user)
        response = admin.get(path)
        assert response.status_code == status.HTTP_200_OK
        obj = parse(response)
        assert obj is not None

    def test_admin_can_add(self, admin_user, game_data):
        path = reverse('game-list')
        admin = get_admin(admin_user)

        response = admin.post(path, game_data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_admin_can_delete(self, admin_user, games):
        path = reverse('game-detail', kwargs={'pk': games[0].id})
        admin = get_admin(admin_user)
        response = admin.delete(path)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_admin_can_update(self, admin_user, games, game_data):
        path = reverse('game-detail', kwargs={'pk': games[0].id})
        admin = get_admin(admin_user)

        response = admin.put(path, game_data, format='multipart')
        assert response.status_code == status.HTTP_200_OK