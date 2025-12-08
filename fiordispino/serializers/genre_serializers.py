from rest_framework import serializers

from fiordispino.models import Genre

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name")
        model = Genre