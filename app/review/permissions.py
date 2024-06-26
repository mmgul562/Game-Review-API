from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsSuperUserOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user and (request.user.is_superuser or
                                 obj.user == request.user)
