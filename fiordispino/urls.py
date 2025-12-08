from django.urls import path
from rest_framework.routers import SimpleRouter

from fiordispino.views.genre_views import GenreViewSet

'''
urlpatterns = [
    path('<int:pk>', GenreDetail.as_view()), # primary key to see a specific genre
    path('', GenreList.as_view()), # empty path to list all genres 
]
'''

router = SimpleRouter()
router.register('genre', GenreViewSet)

urlpatterns = router.urls