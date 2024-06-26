from rest_framework import serializers

from core.models import Game, GameRequest


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


class GameRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameRequest
        fields = ['id', 'title', 'developer', 'duration',
                  'release_date', 'in_early_access', 'has_multiplayer',
                  'created_at', 'rejected', 'feedback']
        read_only_fields = ['id', 'created_at', 'rejected', 'feedback']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request', None)
        user = request.user if request else None

        if user and not user.is_superuser:
            if not instance.rejected:
                representation.pop('feedback', None)

        return representation
