from rest_framework import serializers

from fiordispino.models import GamesToPlay


class GamesToPlaySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'owner', 'games')
        model = GamesToPlay