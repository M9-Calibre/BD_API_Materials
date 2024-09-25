from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        return obj.submitted_by == request.user


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff

class IsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.submitted_by == request.user
## Permissions for Groups
class IsAdminOrOwnerOrGroupCanInteract(permissions.BasePermission):

    # def has_permission(self, request, view):
    #     print("sussy baka 2")
    #     if request.method in permissions.SAFE_METHODS:
    #         return True
    def has_object_permission(self, request, view, obj):
        print("sussy baka")
        request_user = request.user
        if request_user.is_staff:
            return True
        if obj.submitted_by == request_user:
            return True
        if request.method in permissions.SAFE_METHODS and not obj.private:
            return True

        # Filter if it is test or a material parameter object
        obj_type = type(obj)
        print(f"{obj_type}")

        if request.method == "GET":
            # See if there is a group in common between the permissions and the user
            return set(request_user.can_read_tests) & set(obj.read_groups)
        elif request.method == "POST":
            return set(request_user.can_edit_tests) & set(obj.edit_groups)
        elif request.method == "DELETE":
            return set(request_user.can_delete_tests) & set(obj.delete_groups)

        return False
