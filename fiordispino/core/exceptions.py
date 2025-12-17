from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.exceptions import APIException


# They have to extend ValidationError because it's the standard in django

class VoteException(ValidationError):
    help_message = "Error in creating vote"

class PegiException(ValidationError):
    help_message = "Error in creating PEGI ranking"


### PUBLISHER EXCEPTIONS ###
class PublisherException(ValidationError):
    help_message = "Error in creating publisher"

class NoPublisherProvided(PublisherException):
    pass

class PublisherMustBeCapitalized(PublisherException):
    pass

class PublisherTooLong(PublisherException):
    pass


### GAME TITLE ###
class GameTitleException(ValidationError):
    help_message = "Error in creating game title"

class NoTitleProvided(GameTitleException):
    pass


### GENRE ###
class GenreException(ValidationError):
    help_message = "Error in creating genre"

class NoGenreProvided(GenreException):
    pass

class GenreTooLong(GenreException):
    pass


### DESCRIPTION ###
class GameDescriptionException(ValidationError):
    help_message = "Error in creating game description"

class NoDescriptionProvided(GameDescriptionException):
    pass

class DescriptionTooLong(GameDescriptionException):
    pass


### GAMES TO PLAY/GAMES PLAYED ####

class GameAlreadyInGamesToPlay(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Before adding this game to the games played list please remove it from the game to play list."
    default_code = 'game_already_in_to_play'

class GameAlreadyInGamesPlayed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Before adding this game to the games to play list please remove it from the games played list."
    default_code = 'game_already_in_played'


### GLOBAL RATING ####
class GlobalRatingException(ValidationError):
    help_message = "Error in creating global rating"


### IMAGE TO BASE64 ENCODER ###
class ImageEncoderException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Error in creating box art image"
    default_code = 'image_encoder_error'


### USERNAME ###
class UsernameValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid username"
    default_code = 'username_error'


### RANDOM GAMES PARAMETER ###
class InvalidNumberOfGamesException(APIException):
     status_code = status.HTTP_400_BAD_REQUEST
     default_detail = "Number of games must be between 1 and 20"
     default_code = 'invalid_n_games'

### IMAGES FORMAT ###
class InvalidImageFormatException(ValidationError):
    help_message = "Error in creating box art image, note that the image format must be jpg"