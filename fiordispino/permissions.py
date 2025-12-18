from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allows access only to admin users for unsafe methods (POST, PUT, DELETE).
    Safe methods (GET, HEAD, OPTIONS) are allowed for everyone.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_staff)


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to allow only owners of an object or admins to edit/delete it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_permission(self, request, view):
        # Allow read-only methods for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # For any write operation, the user must be authenticated
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object OR staff users
        return obj.owner == request.user or bool(request.user and request.user.is_staff)


class IsAdminUnlessMe(permissions.BasePermission):
    """
    Specific permission class for the user endpoints, the logic is: every endpoint is reserved to the admin except for the one that returns info about me
    """

    def has_permission(self, request, view):
        if view.action == 'get_current_user_data':
            return bool(request.user and request.user.is_authenticated)

        return bool(request.user and request.user.is_staff)


# --- DJANGO ADMIN PERMISSIONS ---
# these permissions are used in admin.py, meaning that they will never by covered by the coverage command.
# Hence, we use pragma: no cover to tell coverage to ignore them

def forbid_add_permission(model_admin, request):  # pragma: no cover
    # prevents the admin from manually creating entries for users
    return False

def forbid_change_permission(model_admin, request, obj=None):  # pragma: no cover
    # prevents the admin from editing existing entries
    return False

def allow_delete_permission(model_admin, request, obj=None):  # pragma: no cover
    # allows the admin to delete entries via the Django Admin panel -> otherwise the admin can't delete games!
    return True