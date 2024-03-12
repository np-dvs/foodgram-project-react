from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """Данные может изменять только админ."""

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_stuff)


class IsAuthorOrReadOnly(BasePermission):
    """Данные может изменять только автор."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.author
