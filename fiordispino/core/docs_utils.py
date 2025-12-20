from rest_framework import serializers
from fiordispino.serializers.game_serializer import GameSerializer
from fiordispino.serializers.games_played_serializer import GamesPlayedSerializer
from fiordispino.serializers.games_to_play_serializer import GamesToPlaySerializer

# shadow serializers to generate realistic docs values

class GameDocsSerializer(GameSerializer):
    pegi = serializers.ChoiceField(choices=[3, 7, 12, 16, 18])
    global_rating = serializers.FloatField(min_value=0.0, max_value=10.0, read_only=True)
    id = serializers.IntegerField(min_value=1, max_value=99999, read_only=True)
    rating_count = serializers.IntegerField(min_value=0, max_value=500000, read_only=True)

    class Meta(GameSerializer.Meta):
        ref_name = 'GameResponseFixed'


class GamesToPlayResponseSerializer(GamesToPlaySerializer):
    game = GameDocsSerializer(read_only=True)
    id = serializers.IntegerField(min_value=1, max_value=99999, read_only=True)

    class Meta(GamesToPlaySerializer.Meta):
        ref_name = 'GamesToPlayResponseFixed'


class GamesPlayedResponseSerializer(GamesPlayedSerializer):
    game = GameDocsSerializer(read_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=10)
    id = serializers.IntegerField(min_value=1, max_value=99999, read_only=True)

    class Meta(GamesPlayedSerializer.Meta):
        ref_name = 'GamesPlayedResponseFixed'