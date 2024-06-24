from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class UsernameOrEmailBackend(BaseBackend):
    def authenticate(self, request, identifier=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(Q(username=identifier) | Q(email=identifier))
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
