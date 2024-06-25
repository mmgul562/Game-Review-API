from rest_framework import serializers

from core.models import Game


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'title', 'developer', 'duration',
                  'release_date', 'in_early_access', 'has_multiplayer']
        read_only_fields = ['id']


class GameListSerializer(serializers.ModelSerializer):
    """
    This serializer is NOT used for listing games themselves.
    Its only purpose is to be used with ReviewListSerializer.
    """
    class Meta:
        model = Game
        fields = ['id', 'title']  # will add picture later
        read_only_fields = ['id']
