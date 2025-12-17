from rest_framework import serializers

from fiordispino.models import Game
from fiordispino.core.utils import encode_image_to_base64
from fiordispino.serializers.genre_serializers import GenreSerializer


class GameSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        fields = ("id", "box_art", "description", "title", "genres", "pegi", "release_date", "global_rating", "rating_count")
        model = Game

    def to_representation(self, instance):
        # this method is called whenever the object has to be serialized to json
        # it first serialize it normally and then overwrites the path to the image with the base64 version of the image

        ret = super().to_representation(instance)

        ret['box_art'] = encode_image_to_base64(instance.box_art)

        return ret