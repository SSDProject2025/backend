from rest_framework import permissions

# this class represents the permission class for users that leaves reviews:
# - you left the review -> you can edit
# - you did not left the review -> you can just read
class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


# permission class that represents objects like games and genres:
# you are not an admin? You can only visualize
# you are an admin? You can do wathever you want
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_staff)

# probably this is redudant because the first one should suffice
class IsLibraryOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='library_owner').exists()


from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or delete it.

    Rules:
    - READ (GET): Everyone can see the entries.
    - CREATE (POST): Any authenticated user can create an entry (add a game).
    - UPDATE (PUT/PATCH): Only the owner of the entry can update it (e.g., change rating).
    - DELETE: Only the owner of the entry can delete it (remove the game).
    """

    def has_permission(self, request, view):
        # Allow read-only methods for everyone (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write operations (POST, PUT, DELETE), the user must be logged in.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow read-only methods for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # For UPDATE and DELETE, check if the user making the request is actually the owner of the object.
        return obj.owner == request.user


def forbid_add_permission(model_admin, request):
    # to prevent the admin from creating libraries
    return False

def forbid_change_permission(model_admin, request, obj=None):
    # to prevent the admin from editing libraries
    return False

def forbid_delete_permission(model_admin, request, obj=None):
    return False
