from django.urls import path, include
from rest_framework.routers import DefaultRouter

from game import views


router = DefaultRouter()
router.register('games', views.GameViewSet)
router.register('game-requests', views.GameRequestViewSet)

app_name = 'game'

urlpatterns = [
    path('', include(router.urls)),
]
