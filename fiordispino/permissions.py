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

