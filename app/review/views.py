from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from core.models import Review
from review.serializers import ReviewListSerializer, ReviewSerializer
from review.permissions import IsOwnerOrReadOnly, IsSuperUserOrOwner


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action in ['destroy']:
            self.permission_classes = [IsAuthenticatedOrReadOnly,
                                       IsSuperUserOrOwner]
        else:
            self.permission_classes = [IsAuthenticatedOrReadOnly,
                                       IsOwnerOrReadOnly]
        return super().get_permissions()

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset.order_by('-id')
        if self.action in ['list', 'retrieve']:
            return self.queryset.order_by('-id')
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return ReviewListSerializer
        return self.serializer_class
