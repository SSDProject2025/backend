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

from rest_framework import permissions


class IsLibraryOwnerUpdateOnly(permissions.BasePermission):
    """
    - READ (GET): everyone can see
    - CREATE (POST): no one can add more libraries -> every user has just a to-play and played library
    - DELETE: no one can delete a library
    - UPDATE (PUT/PATCH): only the owner can edit library
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method in ['PUT', 'PATCH']:
            return request.user and request.user.is_authenticated

        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method in ['PUT', 'PATCH']:
            return obj.owner == request.user

        return False


def forbid_add_permission(model_admin, request):
    # to prevent the admin from creating libraries
    return False

def forbid_change_permission(model_admin, request, obj=None):
    # to prevent the admin from editing libraries
    return False

def forbid_delete_permission(model_admin, request, obj=None):
    return False
