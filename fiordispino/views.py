from rest_framework import generics, viewsets

from fiordispino.models import Genre, Game
from fiordispino.serializers import GenreSerializer
from fiordispino.serializers.game_serializer import GameSerializer
from fiordispino import permissions

'''
class GenreList(generics.ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

class GenreDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
'''

# use a single view class to replace multiple views
class GenreViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminOrReadOnly]
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

class GameViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminOrReadOnly]
    queryset = Game.objects.all()
    serializer_class = GameSerializer