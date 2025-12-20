import pytest
from django.urls import reverse
from rest_framework import status
from mixer.backend.django import mixer
from django.contrib.auth import get_user_model
from fiordispino.tests.utils_testing import *


@pytest.mark.django_db
class TestUserUrls:

    def test_authenticated_user_can_access_me(self, user):
        path = reverse('user-get-current-user-data')
        client = get_client(user)

        response = client.get(path)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
        assert response.data['email'] == user.email

    def test_admin_can_access_me(self, admin_user):
        path = reverse('user-get-current-user-data')
        client = get_admin(admin_user)

        response = client.get(path)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == admin_user.id

    # --- REGULAR USER RESTRICTIONS ---

    def test_user_cant_list_users(self, user):
        path = reverse('user-list')
        client = get_client(user)

        response = client.get(path)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_cant_retrieve_other_user_details(self, user):
        other_user = mixer.blend(get_user_model())
        path = reverse('user-detail', kwargs={'pk': other_user.id})

        client = get_client(user)

        response = client.get(path)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_cant_delete_other_user(self, user):
        other_user = mixer.blend(get_user_model())
        path = reverse('user-detail', kwargs={'pk': other_user.id})

        client = get_client(user)

        response = client.delete(path)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # --- ADMIN PRIVILEGES (The "IsAdmin" part) ---

    def test_admin_can_list_users(self, admin_user):
        mixer.cycle(3).blend(get_user_model()) # fake users to check for multiple accounts

        path = reverse('user-list')
        client = get_admin(admin_user)

        response = client.get(path)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 3

    def test_admin_can_retrieve_any_user(self, admin_user):
        target_user = mixer.blend(get_user_model())
        path = reverse('user-detail', kwargs={'pk': target_user.id})

        client = get_admin(admin_user)

        response = client.get(path)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == target_user.id

    def test_admin_can_delete_user(self, admin_user):
        target_user = mixer.blend(get_user_model())
        path = reverse('user-detail', kwargs={'pk': target_user.id})

        client = get_admin(admin_user)

        response = client.delete(path)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert get_user_model().objects.filter(pk=target_user.id).exists() is False

    # --- ANONYMOUS TESTS (No Access) ---

    def test_anonymous_cannot_access_me(self):
        path = reverse('user-get-current-user-data')
        client = get_client()

        response = client.get(path)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_anonymous_cannot_list_users(self):
        path = reverse('user-list')
        client = get_client()

        response = client.get(path)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED