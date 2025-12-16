import pytest
from django.urls import reverse
from rest_framework import status
from fiordispino.tests.utils_testing import *


@pytest.mark.django_db
class TestUserView:

    def test_get_current_user_data_success(self, user):
        """
        Verify authenticated user can retrieve their own profile data.
        """
        client = get_client(user)
        url = reverse('user-get-current-user-data')

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK

        data = parse(response)
        assert data['email'] == user.email
        assert data['username'] == user.username
        # Security check: password should never be returned
        assert 'password' not in data

    def test_get_current_user_data_unauthorized(self):
        """
        Verify unauthenticated users cannot access profile data.
        """
        client = get_client(user=None)
        url = reverse('user-get-current-user-data')

        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED