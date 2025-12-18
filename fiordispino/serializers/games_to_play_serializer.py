from rest_framework import serializers
from fiordispino.models import GamesToPlay, GamePlayed
from fiordispino.serializers import game_serializer


class GamesToPlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = GamesToPlay
        fields = ('id', 'owner', 'game', 'created_at')

        # 'owner' is handled by the view (request.user), so it must be read-only here
        # 'created_at' is auto-generated -> I guess it tells you when you completed the game?
        read_only_fields = ['owner', 'created_at']

    # to get the whole game representation instead of just the id
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # If you want the full game details:
        representation['game'] = game_serializer.GameSerializer(instance.game).data

        # if you just want the title:
        # representation['game_title'] = instance.game.title

        return representation


class MoveToPlayedSerializer(serializers.ModelSerializer):
    class Meta:
        model = GamePlayed
        fields = ['rating']
        extra_kwargs = {
            'rating': {'required': True}
        }