from rest_framework import serializers

from fiordispino.models import GamesToPlay, Game


class GamesToPlaySerializer(serializers.ModelSerializer):

    # Explicitly handles the ManyToMany relationship by accepting and validating
    # a list of Game IDs (PKs) against the database for write operations.
    games = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Game.objects.all()
    )

    class Meta:
        fields = ('id', 'owner', 'games')
        model = GamesToPlay

        # otherwise owner would be requested in the put!
        read_only_fields = ['owner']