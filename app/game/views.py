from rest_framework import (viewsets,
                            permissions,
                            authentication)
from rest_framework.exceptions import PermissionDenied

from core.models import Game
from game.permissions import IsSuperUser
from game.serializers import GameSerializer


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsSuperUser]
        elif self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
        return super(GameViewSet, self).get_permissions()

    def perform_create(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only superusers can add games directly.")
        serializer.save()
