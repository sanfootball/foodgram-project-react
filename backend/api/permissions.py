from rest_framework.permissions import BasePermission, SAFE_METHODS


class AnonimOrAuthenticatedReadOnly(BasePermission):
    """Разрешает анонимному пользователю только безопасные запросы."""

    def has_object_permission(self, request, view, object):
        return (
            (request.method in SAFE_METHODS and (
                request.user.is_anonymous
                or request.user.is_authenticated))
            or request.user.is_superuser
            or request.user.is_staff
        )


class AuthorOrReadOnly(BasePermission):
    """Предоставляет право создавать/редактировать/удалять
    собственные рецепты только автору объекта,
    неавторизованному пользователю только на чтение объектов."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user
