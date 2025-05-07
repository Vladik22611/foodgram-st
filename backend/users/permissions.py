from rest_framework import permissions


class IsAuthenticatedOrReadOnlyForMe(permissions.BasePermission):
    """
    Пермишн, который позволяет авторизованным
    пользователям изменять свои данные,
    а неавторизованные могут только просматривать данные.

    Разрешает доступ к действию 'me' только для авторизованных пользователей.
    """

    def has_permission(self, request, view):

        # Разрешаем доступ к действию 'me' только для авторизованных пользователей
        if view.action == "me":
            return request.user and request.user.is_authenticated

        # Для всех остальных действий разрешаем доступ только для анонимных пользователей
        return request.method in permissions.SAFE_METHODS
