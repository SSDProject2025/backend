from rest_framework.routers import SimpleRouter

from fiordispino.views import GenreViewSet, GameViewSet, GamesToPlayViewSet

'''
urlpatterns = [
    path('<int:pk>', GenreDetail.as_view()), # primary key to see a specific genre
    path('', GenreList.as_view()), # empty path to list all genres 
]
'''

router = SimpleRouter()
router.register('genre', GenreViewSet, basename='genre')
router.register('game', GameViewSet, basename='game')
router.register(r'games-to-play', GamesToPlayViewSet, basename='games-to-play')

urlpatterns = router.urls