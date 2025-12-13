from rest_framework import serializers

from fiordispino.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("username", "email", "password")
        model = User