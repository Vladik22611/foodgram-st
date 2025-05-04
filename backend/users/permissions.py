from rest_framework import permissions


class IsAuthenticatedOrReadOnlyForMe(permissions.BasePermission):
    def has_permission(self, request, view):
        # Разрешаем GET /users/me только для авторизованных
        if view.action == "me":
            return request.user and request.user.is_authenticated
        # Для всех остальных действий используем стандартные правила
        return True
