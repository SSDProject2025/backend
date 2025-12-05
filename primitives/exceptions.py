class GameTitleException(Exception):
    help_message = "Error in creating game title"

class VoteException(Exception):
    help_message = "Error in creating vote"

class PegiException(Exception):
    help_message = "Error in creating PEGI ranking"

class PublisherException(Exception):
    help_message = "Error in creating publisher"