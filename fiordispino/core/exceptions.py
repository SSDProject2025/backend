from django.core.exceptions import ValidationError

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

class GameAlreadyInGamesToPlay(ValidationError):
    help_message = "Before adding this game to the the games played list please remove it from the game to play list"

class GameAlreadyInGamesPlayed(ValidationError):
    help_message = "Before adding this game the games to play list please remove it from the games played list"