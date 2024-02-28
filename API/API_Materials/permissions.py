from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        print("very sussy")
        if request.method in permissions.SAFE_METHODS:
            print("sus")
            return True
        if request.user.is_staff:
            return True
        return obj.submitted_by == request.user


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff
