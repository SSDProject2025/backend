from rest_framework import serializers

from fiordispino.models import Game

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "box_art", "description", "title", "genres", "pegi", "release_date")
        model = Game