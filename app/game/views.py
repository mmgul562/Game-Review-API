from rest_framework import (viewsets,
                            permissions,
                            authentication,
                            status)
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone

from core.models import Game, GameRequest
from game.permissions import IsSuperUser
from game.serializers import GameSerializer, GameRequestSerializer


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


class GameRequestViewSet(viewsets.ModelViewSet):
    serializer_class = GameRequestSerializer
    queryset = GameRequest.objects.all()
    authentication_classes = [authentication.TokenAuthentication]

    def get_permissions(self):
        if self.action in ['approve', 'reject']:
            self.permission_classes = [IsSuperUser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        game_request = self.get_object()

        game = Game.objects.create(
            title=game_request.title,
            developer=game_request.developer,
            duration=game_request.duration,
            release_date=game_request.release_date,
            in_early_access=game_request.in_early_access,
            has_multiplayer=game_request.has_multiplayer
        )
        game_request.delete()
        serializer = GameSerializer(game)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        game_request = self.get_object()
        if game_request.rejected:
            return Response(
                {'detail': 'This game request is already rejected.'},
                status.HTTP_405_METHOD_NOT_ALLOWED
            )
        feedback = request.data.get('feedback', '')

        game_request.rejected = True
        game_request.rejections += 1
        game_request.feedback = feedback
        game_request.rejected_at = timezone.now()
        game_request.save()

        return Response({'status': 'rejected',
                        'feedback': feedback}, status=status.HTTP_200_OK)
