from rest_framework import serializers
from fiordispino.models import GamePlayed
from fiordispino.serializers import game_serializer


class GamesPlayedSerializer(serializers.ModelSerializer):
    class Meta:
        model = GamePlayed
        fields = ('id', 'owner', 'game', 'created_at', 'rating')
        read_only_fields = ('owner', 'created_at')

    # to get the whole game representation instead of just the id
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # If you want the full game details:
        representation['game'] = game_serializer.GameSerializer(instance.game).data

        # if you just want the title:
        # representation['game_title'] = instance.game.title

        return representation
