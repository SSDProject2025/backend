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


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or delete it.

    Rules:
    - READ (GET): Everyone can see the entries.
    - CREATE (POST): Any authenticated user can create.
    - UPDATE/DELETE: Only the owner.
    """

    def has_permission(self, request, view):
        # Allow read-only methods for everyone (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write operations (POST, PUT, DELETE), the user must be logged in.
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Allow read-only methods for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # For UPDATE and DELETE, check if the user is the owner
        return obj.owner == request.user


# --- DJANGO ADMIN PERMISSIONS ---
# these permissions are used in admin.py, meaning that they will never by covered by the coverage command.
# Hence, we use pragma: no cover to tell coverage to ignore them

def forbid_add_permission(model_admin, request):  # pragma: no cover
    # to prevent the admin from creating libraries
    return False

def forbid_change_permission(model_admin, request, obj=None):  # pragma: no cover
    # to prevent the admin from editing libraries
    return False

def forbid_delete_permission(model_admin, request, obj=None):  # pragma: no cover
    return False