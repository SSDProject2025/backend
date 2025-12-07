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