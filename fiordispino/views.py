from django.db import transaction
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from fiordispino.models import *
from fiordispino.serializers import GenreSerializer
from fiordispino.serializers.game_serializer import GameSerializer
from fiordispino import permissions
from fiordispino.serializers.games_to_play_serializer import GamesToPlaySerializer
from fiordispino.serializers.games_played_serializer import GamesPlayedSerializer
from fiordispino.core.exceptions import GameAlreadyInGamesToPlay, GameAlreadyInGamesPlayed

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

    # add method to serialize image in base 64


# do retrieve to check for game in libraries
class GamesToPlayViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsOwnerOrReadOnly]
    queryset = GamesToPlay.objects.all()
    serializer_class = GamesToPlaySerializer

    def perform_create(self, serializer):
        user = self.request.user
        game_ = serializer.validated_data['game']

        # do not add the game if it is already in the games played entity
        if GamePlayed.objects.filter(owner=user, game=game_).exists():
            raise GameAlreadyInGamesPlayed(
                {"detail": GameAlreadyInGamesPlayed.help_message}
            )

        serializer.save(owner=user)

    # this custom endpoint is used to easily switch a game to the other table
    @action(detail=True, methods=['post'], url_path='move-in-played')
    def move_to_played(self, request, pk=None):
        game_to_play_instance = self.get_object()

        # you need the rating to add to game played
        rating = request.data.get('rating')
        if rating is None:
            return Response(
                {"detail": "Please provide a rating for this game."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # atomic means do all or do nothing: if something goes wrong perform a rollback
        with transaction.atomic():
            GamePlayed.objects.create(
                owner=game_to_play_instance.owner,
                game=game_to_play_instance.game,
                rating=rating
            )

            game_to_play_instance.delete()

        return Response(status=status.HTTP_200_OK)

class GamePlayedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsOwnerOrReadOnly]
    queryset = GamePlayed.objects.all()
    serializer_class = GamesPlayedSerializer

    def perform_create(self, serializer):
        user = self.request.user
        game_ = serializer.validated_data['game']

        # do not add the game if it is already in the games to play entity
        if GamesToPlay.objects.filter(owner=user, game=game_).exists():
            raise GameAlreadyInGamesToPlay(
                {"detail": GameAlreadyInGamesToPlay.help_message}
            )

        # Se il controllo passa, salva iniettando l'owner
        serializer.save(owner=user)

    @action(detail=True, methods=['post'], url_path='move-in-to-play')
    def move_to_backlog(self, request, pk=None):
        played_instance = self.get_object()

        with transaction.atomic():
            GamesToPlay.objects.create(
                owner=played_instance.owner,
                game=played_instance.game
            )

            played_instance.delete()

        return Response(status=status.HTTP_200_OK)