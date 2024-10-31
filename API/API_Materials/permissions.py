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

        user_groups = request_user.user_groups.all()
        user_groups_ids = []

        for user_group in user_groups:
            user_groups_ids.append(user_group.id)

        if request.method == "GET":
            # See if there is a group in common between the permissions and the user group
            for read_group in obj.read_groups.all():
                if read_group.id in user_groups_ids: return True
                # if set(user_groups_ids) & set(obj.read_groups.all()): return True
            return False

        elif request.method == "POST":
            for edit_group in obj.edit_groups.all():
                if edit_group.id in user_groups_ids: return True
            return False

        elif request.method == "DELETE":
            for delete_group in obj.delete_groups.all():
                if delete_group.id in user_groups_ids: return True
            return False

        return False
