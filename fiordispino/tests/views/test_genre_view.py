import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from mixer.backend.django import mixer
from django.contrib.auth import get_user_model  # Import necessario per creare l'admin
from fiordispino.views import GenreViewSet
from fiordispino.models import Genre

"""
notes on view test:
when you test url, you can istantiate an API client which simulate a call; when you test a view you have to manually configure the request.
"""


@pytest.mark.django_db
class TestGenreView:

    # Aggiungiamo la fixture per l'admin, come fatto per Game
    @pytest.fixture
    def admin_user(self):
        return mixer.blend(get_user_model(), is_staff=True, is_superuser=True)

    def test_list_genres_view(self):
        # create dummy data
        mixer.blend(Genre, name="Action")
        mixer.blend(Genre, name="Adventure")
        mixer.blend(Genre, name="RPG")

        # as you can see, the url is actually meaningless in this context: we're creating a fake request
        factory = APIRequestFactory()
        request = factory.get('/fake-url/')

        # here we are specifying which action to map
        view = GenreViewSet.as_view({'get': 'list'})

        response = view(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_create_genre_view(self, admin_user):  # Passiamo admin_user qui
        # similar to the above method, but this time we're testing the creation

        factory = APIRequestFactory()
        data = {'name': 'Steampunk'}
        request = factory.post('/fake-url/', data)

        # if the view needed auth, you could use:
        # user = mixer.blend('auth.User')
        # force_authenticate(request, user=user)

        # ORA APPLICHIAMO L'AUTENTICAZIONE REALE QUI SOTTO:
        force_authenticate(request, user=admin_user)

        view = GenreViewSet.as_view({'post': 'create'})
        response = view(request)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Steampunk'
        assert Genre.objects.count() == 1