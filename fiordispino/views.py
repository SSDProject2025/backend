from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView

from fiordispino.models import *
from fiordispino.serializers import GenreSerializer
from fiordispino.serializers.game_serializer import GameSerializer
from fiordispino import permissions
from fiordispino.serializers.games_to_play_serializer import GamesToPlaySerializer
from fiordispino.serializers.games_played_serializer import GamesPlayedSerializer
from fiordispino.core.exceptions import GameAlreadyInGamesToPlay, GameAlreadyInGamesPlayed

from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.db import IntegrityError

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
            raise GameAlreadyInGamesPlayed()

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
            raise GameAlreadyInGamesToPlay()

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

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password1 = request.data.get('password1')
        password2 = request.data.get('password2')

        # Validazioni
        if not email or not password1:
            return Response(
                {'error': 'Email e password sono richiesti'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if password1 != password2:
            return Response(
                {'error': 'Le password non coincidono'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Controlla se email esiste già
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Questa email è già registrata'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Crea l'utente
            user = User.objects.create_user(
                username=email,  # Usa email come username
                email=email,
                password=password1
            )

            # Crea il token
            token = Token.objects.create(user=user)

            return Response({
                'key': token.key
            }, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response(
                {'error': 'Questa email è già registrata'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Errore durante la registrazione: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Email e password sono richiesti'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, email=email, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'key': token.key
            })

        return Response(
            {'error': 'Credenziali non valide'},
            status=status.HTTP_401_UNAUTHORIZED
        )