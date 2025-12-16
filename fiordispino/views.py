from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView

from fiordispino.models import *
from fiordispino.serializers.genre_serializers import GenreSerializer
from fiordispino.serializers.game_serializer import GameSerializer
from fiordispino import permissions
from fiordispino.serializers.games_to_play_serializer import GamesToPlaySerializer
from fiordispino.serializers.games_played_serializer import GamesPlayedSerializer
from fiordispino.core.exceptions import GameAlreadyInGamesToPlay, GameAlreadyInGamesPlayed
from fiordispino.serializers.login_serializers import LoginSerializer
from fiordispino.serializers.register_serializers import RegisterSerializer
from fiordispino.serializers.user_serializer import UserSerializer

from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

from rest_framework.permissions import IsAuthenticated

from fiordispino.core.validators import validate_username, validate_random_games_limit

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

    @action(detail=False, methods=['get'], url_path='random-games')
    def get_random_games(self, request):
        raw_n = request.query_params.get('n_games', "5") # default to 5 if no value passed -> it's a string because the validator expect a string from the api

        validate_random_games_limit(raw_n)

        n_games = int(raw_n)

        games = Game.objects.order_by('?')[:n_games]
        serializer = self.get_serializer(games, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# do retrieve to check for game in libraries
class GamesToPlayViewSet(viewsets.ModelViewSet):

    # you can see other users' libraries only if you are authenticated
    permission_classes = [IsAuthenticated, permissions.IsOwnerOrReadOnly]
    queryset = GamesToPlay.objects.all()
    serializer_class = GamesToPlaySerializer

    def perform_create(self, serializer):
        user_ = self.request.user
        game_ = serializer.validated_data['game']

        # do not add the game if it is already in the games played entity
        if GamePlayed.objects.filter(owner=user_, game=game_).exists():
            raise GameAlreadyInGamesPlayed()

        serializer.save(owner=user_)

    # to capture the username I need a regex that says -> take everything till you meet a '/' ora a '.'
    @action(detail=False, methods=['get'], url_path=r'owner/(?P<username>[^/.]+)')
    def get_by_owner(self, request, username=None):

        validate_username(username)

        games = GamesToPlay.objects.filter(owner__username=username)

        serializer_ = self.get_serializer(games, many=True)
        return Response(serializer_.data, status=status.HTTP_200_OK)


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
    permission_classes = [IsAuthenticated, permissions.IsOwnerOrReadOnly]
    queryset = GamePlayed.objects.all()
    serializer_class = GamesPlayedSerializer

    def perform_create(self, serializer):
        user_ = self.request.user
        game_ = serializer.validated_data['game']

        # do not add the game if it is already in the games to play entity
        if GamesToPlay.objects.filter(owner=user_, game=game_).exists():
            raise GameAlreadyInGamesToPlay()

        # Se il controllo passa, salva iniettando l'owner
        serializer.save(owner=user_)

    @action(detail=False, methods=['get'], url_path=r'owner/(?P<username>[^/.]+)')
    def get_by_owner(self, request, username=None):

        validate_username(username)

        games = GamePlayed.objects.filter(owner__username=username)

        serializer_ = self.get_serializer(games, many=True)
        return Response(serializer_.data, status=status.HTTP_200_OK)

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

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer  # Utile per la documentazione automatica

    def post(self, request):
        data = request.data.copy()
        if 'password1' in data:
            data['password'] = data['password1']

        serializer = RegisterSerializer(data=data)

        if serializer.is_valid():
            user_ = serializer.save()

            # Crea o recupera il token
            token, created = Token.objects.get_or_create(user=user_)

            return Response({
                'key': token.key
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user_ = authenticate(request, username=email, password=password)

        if user_:
            token, created = Token.objects.get_or_create(user=user_)
            return Response({'key': token.key}, status=status.HTTP_200_OK)

        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Endpoint: /api/v1/users/me/
    @action(detail=False, methods=['get'], url_path='me')
    def get_current_user_data(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
