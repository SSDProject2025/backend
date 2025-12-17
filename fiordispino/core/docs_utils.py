from rest_framework import serializers
from fiordispino.serializers.game_serializer import GameSerializer
from fiordispino.serializers.games_played_serializer import GamesPlayedSerializer

# shadow serializers to generate valid documentation with realisitc data

class GameDocsSerializer(GameSerializer):
    pegi = serializers.ChoiceField(choices=[3, 7, 12, 16, 18])
    global_rating = serializers.FloatField(min_value=0.0, max_value=10.0, read_only=True)
    id = serializers.IntegerField(min_value=1, max_value=99999, read_only=True)
    rating_count = serializers.IntegerField(min_value=0, max_value=500000, read_only=True)

    class Meta(GameSerializer.Meta):
        ref_name = 'GameResponseFixed'

class GamesPlayedDocsSerializer(GamesPlayedSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=10)
    id = serializers.IntegerField(min_value=1, max_value=99999, read_only=True)

    class Meta(GamesPlayedSerializer.Meta):
        ref_name = 'GamePlayedResponseFixed'