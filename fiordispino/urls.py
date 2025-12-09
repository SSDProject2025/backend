from django.urls import path
from rest_framework.routers import SimpleRouter

from fiordispino.views.views import GenreViewSet, GameViewSet

'''
urlpatterns = [
    path('<int:pk>', GenreDetail.as_view()), # primary key to see a specific genre
    path('', GenreList.as_view()), # empty path to list all genres 
]
'''

router = SimpleRouter()
router.register('genre', GenreViewSet, basename='genre')
router.register('game', GameViewSet, basename='game')

urlpatterns = router.urls