from rest_framework import serializers

from fiordispino.models import Game, Genre
from fiordispino.core.utils import encode_image_to_base64
from fiordispino.serializers.genre_serializers import GenreSerializer


class GameSerializer(serializers.ModelSerializer):
    genres = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Genre.objects.all()
    )

    class Meta:
        fields = ("id", "box_art", "description", "title", "genres", "pegi", "release_date", "global_rating", "rating_count")
        model = Game

    def to_representation(self, instance):
        # Quando serializzi (GET), usa GenreSerializer per mostrare oggetti completi
        ret = super().to_representation(instance)
        ret['box_art'] = encode_image_to_base64(instance.box_art)
        ret['genres'] = GenreSerializer(instance.genres.all(), many=True).data
        return ret