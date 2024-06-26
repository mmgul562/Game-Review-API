from rest_framework import serializers

from core.models import Review, Game
from game.serializers import (GameSerializer,
                              GameListSerializer)


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed review.
    Includes `body` field and detailed game data.
    """
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all())

    class Meta:
        model = Review
        fields = ['id', 'title', 'game', 'body', 'rating', 'hours_played',
                  'percent_finished', 'played_with_friends']
        read_only_fields = ['id']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['game'] = GameSerializer(instance.game).data
        return ret


class ReviewListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing reviews.
    Doesn't include `body` field or detailed game data.
    """
    game = GameListSerializer(required=True)

    class Meta:
        model = Review
        fields = ['id', 'title', 'game', 'rating', 'hours_played',
                  'percent_finished', 'played_with_friends']
        read_only_fields = ['id']
