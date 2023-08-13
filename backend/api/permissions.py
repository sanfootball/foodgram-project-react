from rest_framework import permissions


class AnonimOrAuthenticatedReadOnly(permissions.BasePermission):
    """Разрешает неавторизованному или авторизованному пользователю
    только безопасные запросы."""

    def has_object_permission(self, request, view, object):
        return (
            (request.method in permissions.SAFE_METHODS and (
                request.user.is_anonymous
                or request.user.is_authenticated))
            or request.user.is_superuser
            or request.user.is_staff
        )
