from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import serializers

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes, inline_serializer, OpenApiExample

from fiordispino.models import *
from fiordispino.serializers.genre_serializers import GenreSerializer
from fiordispino.serializers.game_serializer import GameSerializer
from fiordispino import permissions as custom_permissions
from fiordispino.serializers.games_to_play_serializer import GamesToPlaySerializer
from fiordispino.serializers.games_played_serializer import GamesPlayedSerializer
from fiordispino.core.exceptions import GameAlreadyInGamesToPlay, GameAlreadyInGamesPlayed
from fiordispino.serializers.login_serializers import LoginSerializer
from fiordispino.serializers.register_serializers import RegisterSerializer
from fiordispino.serializers.user_serializer import UserSerializer
from fiordispino.core.validators import validate_username, validate_random_games_limit
from fiordispino.permissions import IsAdminUnlessMe


from fiordispino.core.docs_utils import GameDocsSerializer, GamesPlayedDocsSerializer

User = get_user_model()

# --- GENRE VIEWSET ---
@extend_schema_view(
    list=extend_schema(
        summary="List all genres",
        description="Returns a list of all available game genres.",
        examples=[
            OpenApiExample(
                'Genre List Example',
                summary='Genre List',
                value=[
                    {'id': 1, 'name': 'RPG'},
                    {'id': 2, 'name': 'Action-Adventure'},
                    {'id': 3, 'name': 'Indie'}
                ],
                response_only=True
            )
        ]
    ),
    create=extend_schema(summary="Create a genre", description="Adds a new genre (Admin only)."),
    retrieve=extend_schema(summary="Retrieve genre details", description="Returns details of a specific genre."),
    update=extend_schema(summary="Update a genre", description="Updates a genre completely (Admin only)."),
    partial_update=extend_schema(summary="Partially update a genre", description="Updates specific fields (Admin only)."),
    destroy=extend_schema(summary="Delete a genre", description="Removes a genre (Admin only)."),
)
class GenreViewSet(viewsets.ModelViewSet):
    permission_classes = [custom_permissions.IsAdminOrReadOnly]
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


# --- GAME VIEWSET ---
@extend_schema_view(
    list=extend_schema(
        summary="List all games",
        description="Returns a paginated list of all games.",
        responses={200: GameDocsSerializer(many=True)}  # Uses Shadow Serializer from docs_utils
    ),
    create=extend_schema(
        summary="Create a game",
        description="Adds a new game to the database (Admin only). Note that the box_art MUST be jpg",
        request=GameDocsSerializer, # Uses Shadow Serializer for validation docs
        examples=[
            OpenApiExample(
                'Game Create Payload',
                summary='Creation Example',
                description='Valid payload to create a game.',
                value={
                    "title": "Hollow Knight",
                    "description": "An epic adventure through a ruined kingdom of insects and heroes.",
                    "genres": [3, 5],
                    "pegi": 7,
                    "release_date": "2017-02-24",
                    "box_art": "hollow_knight.jpg"
                },
                request_only=True
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Retrieve game details",
        description="Returns full details of a specific game.",
        responses={200: GameDocsSerializer}, # Uses Shadow Serializer
        examples=[
            OpenApiExample(
                'Game Detail Example',
                summary='Realistic Game Detail',
                description='Example of GET response with valid data (PEGI enum, Rating 0-10).',
                value={
                    "id": 101,
                    "title": "The Witcher 3: Wild Hunt",
                    "description": "A story-driven open world RPG set in a visually stunning fantasy universe.",
                    "genres": [
                        {"id": 1, "name": "RPG"},
                        {"id": 2, "name": "Action"}
                    ],
                    "pegi": 18,
                    "release_date": "2015-05-19",
                    "global_rating": 9.8,
                    "rating_count": 45200,
                    "box_art": "witcher3.jpg"
                },
                response_only=True,
                status_codes=[200]
            )
        ]
    ),
    update=extend_schema(
        summary="Update a game",
        description="Updates a game completely. (Admin only)",
        request=GameDocsSerializer
    ),
    partial_update=extend_schema(
        summary="Partially update a game",
        description="Updates specific fields. (Admin only)",
        request=GameDocsSerializer
    ),
    destroy=extend_schema(summary="Delete a game", description="Removes a game. (Admin only)"),
)
class GameViewSet(viewsets.ModelViewSet):
    permission_classes = [custom_permissions.IsAdminOrReadOnly]
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    @extend_schema(
        summary="Get random games",
        description="Returns a list of random games.",
        parameters=[
            OpenApiParameter(
                name='n_games',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of random games (Default: 5; Min: 1; Max: 20).',
                required=False
            )
        ],
        responses={200: GameDocsSerializer(many=True)} # Uses Shadow Serializer
    )
    @action(detail=False, methods=['get'], url_path='random-games')
    def get_random_games(self, request):
        raw_n = request.query_params.get('n_games', "5")
        validate_random_games_limit(raw_n)
        n_games = int(raw_n)

        games = Game.objects.order_by('?')[:n_games]
        serializer = self.get_serializer(games, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --- GAMES TO PLAY VIEWSET ---
@extend_schema_view(
    list=extend_schema(summary="List 'Games to Play'", description="Returns the backlog list."),
    create=extend_schema(
        summary="Add to 'Games to Play'",
        description="Adds a game to the backlog.",
        examples=[
            OpenApiExample(
                'Add to Backlog',
                summary='Add Game',
                value={"game": 101},
                request_only=True
            )
        ]
    ),
    retrieve=extend_schema(summary="Retrieve entry details"),
    update=extend_schema(summary="Update entry"),
    partial_update=extend_schema(summary="Partially update entry"),
    destroy=extend_schema(summary="Remove from 'Games to Play'"),
)
class GamesToPlayViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, custom_permissions.IsOwnerOrReadOnly]
    queryset = GamesToPlay.objects.all()
    serializer_class = GamesToPlaySerializer

    def perform_create(self, serializer):
        user_ = self.request.user
        game_ = serializer.validated_data['game']
        if GamePlayed.objects.filter(owner=user_, game=game_).exists():
            raise GameAlreadyInGamesPlayed()
        serializer.save(owner=user_)

    @extend_schema(
        summary="Get games to play by owner",
        description="Returns the 'Games to Play' list for a specific user.",
        responses={200: GamesToPlaySerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path=r'owner/(?P<username>[^/.]+)')
    def get_by_owner(self, request, username=None):
        validate_username(username)
        games = GamesToPlay.objects.filter(owner__username=username)
        serializer_ = self.get_serializer(games, many=True)
        return Response(serializer_.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Move to 'Games Played'",
        description="Moves a game to 'Games Played'. Requires a rating.",
        request=inline_serializer(
            name='MoveToPlayedRequest',
            fields={
                # Forced constraints for 1-10 rating
                'rating': serializers.IntegerField(help_text="Rating (1-10)", min_value=1, max_value=10)
            }
        ),
        examples=[
            OpenApiExample(
                'Rating Payload',
                summary='Rating Example',
                description='The rating must be an integer between 1 and 10.',
                value={"rating": 9},
                request_only=True
            )
        ],
        responses={200: None, 400: None}
    )
    @action(detail=True, methods=['post'], url_path='move-in-played')
    def move_to_played(self, request, pk=None):
        game_to_play_instance = self.get_object()
        rating = request.data.get('rating')
        if rating is None:
            return Response({"detail": "Please provide a rating."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            GamePlayed.objects.create(
                owner=game_to_play_instance.owner,
                game=game_to_play_instance.game,
                rating=rating
            )
            game_to_play_instance.delete()
        return Response(status=status.HTTP_200_OK)


# --- GAMES PLAYED VIEWSET ---
@extend_schema_view(
    list=extend_schema(
        summary="List 'Games Played'",
        description="Returns finished games.",
        responses={200: GamesPlayedDocsSerializer(many=True)} # Uses Shadow Serializer
    ),
    create=extend_schema(
        summary="Add to 'Games Played'",
        description="Adds a finished game with a rating.",
        request=inline_serializer(
            name='GamePlayedCreate',
            fields={
                'game': serializers.IntegerField(min_value=1),
                # Forced constraints for 1-10 rating
                'rating': serializers.IntegerField(min_value=1, max_value=10)
            }
        ),
        examples=[
            OpenApiExample(
                'Add Played Game',
                summary='Creation Example',
                description='Adds a completed game with a rating of 10.',
                value={
                    "game": 101,
                    "rating": 10
                },
                request_only=True
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Retrieve entry details",
        responses={200: GamesPlayedDocsSerializer} # Uses Shadow Serializer
    ),
    update=extend_schema(summary="Update entry", request=GamesPlayedDocsSerializer),
    partial_update=extend_schema(summary="Partially update entry", request=GamesPlayedDocsSerializer),
    destroy=extend_schema(summary="Remove from 'Games Played'"),
)
class GamePlayedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, custom_permissions.IsOwnerOrReadOnly]
    queryset = GamePlayed.objects.all()
    serializer_class = GamesPlayedSerializer

    def perform_create(self, serializer):
        user_ = self.request.user
        game_ = serializer.validated_data['game']
        if GamesToPlay.objects.filter(owner=user_, game=game_).exists():
            raise GameAlreadyInGamesToPlay()
        serializer.save(owner=user_)

    @extend_schema(
        summary="Get played games by owner",
        description="Returns the 'Games Played' list for a specific user.",
        responses={200: GamesPlayedDocsSerializer(many=True)} # Uses Shadow Serializer
    )
    @action(detail=False, methods=['get'], url_path=r'owner/(?P<username>[^/.]+)')
    def get_by_owner(self, request, username=None):
        validate_username(username)
        games = GamePlayed.objects.filter(owner__username=username)
        serializer_ = self.get_serializer(games, many=True)
        return Response(serializer_.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Move back to 'Games to Play'",
        request=None,
        responses={200: None}
    )
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


# --- AUTH VIEWS ---
class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(
        summary="User Registration",
        description="Registers a new user and returns a token.",
        request=RegisterSerializer,
        examples=[
            OpenApiExample(
                'Register Request',
                summary='Registration Data',
                value={
                    "username": "john_darksouls",
                    "email": "johndarksouls@example.com",
                    "password": "SecurePassword123!",
                    "password1": "SecurePassword123!"
                },
                request_only=True
            )
        ],
        responses={
            201: inline_serializer(name='RegisterResponse', fields={'key': serializers.CharField()}),
            400: None
        }
    )
    def post(self, request):
        data = request.data.copy()
        if 'password1' in data:
            data['password'] = data['password1']

        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user_ = serializer.save()
            token, created = Token.objects.get_or_create(user=user_)
            return Response({'key': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        summary="User Login",
        description="Authenticates a user.",
        request=LoginSerializer,
        examples=[
            OpenApiExample(
                'Login Request',
                summary='Credentials',
                value={
                    "email": "johndarksouls@example.com",
                    "password": "SecurePassword123!"
                },
                request_only=True
            )
        ],
        responses={
            200: inline_serializer(name='LoginResponse', fields={'key': serializers.CharField()}),
            400: None,
            401: None
        }
    )
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
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


# --- USER VIEWSET ---
@extend_schema_view(
    list=extend_schema(summary="List users", description="Returns a list of all users (Admin only)."),
    retrieve=extend_schema(summary="Retrieve user details", description="Returns details of a specific user (Admin only)."),
    update=extend_schema(summary="Update user", description="Updates user profile information (Admin only)."),
    partial_update=extend_schema(summary="Partially update user", description="Partially updates user profile (Admin only)."),
    destroy=extend_schema(summary="Delete user", description="Deletes a user account (Admin only)."),
    create=extend_schema(summary="Create user", description="Creates a new user (Admin only)."),
)
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUnlessMe]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @extend_schema(
        summary="Get current user info",
        description="Returns the profile information of the currently authenticated user.",
        responses={200: UserSerializer}
    )
    @action(detail=False, methods=['get'], url_path='me')
    def get_current_user_data(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)