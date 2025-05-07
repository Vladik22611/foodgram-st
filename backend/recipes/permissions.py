from rest_framework import permissions


class RecipePermission(permissions.BasePermission):
    """
    Кастомный permission для рецептов:
    - Чтение разрешено всем (GET, HEAD, OPTIONS)
    - Создание (POST) требует аутентификации (401 если не авторизован)
    - Изменение/удаление (PUT, PATCH, DELETE) разрешено
      только автору (403 если не автор)
    """

    def has_permission(self, request, view):
        # Разрешаем безопасные методы для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для создания рецепта требуется авторизация
        if request.method == "POST":
            return request.user.is_authenticated

        # Для остальных методов проверка будет в has_object_permission
        return True

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Изменение и удаление разрешено только автору
        return obj.author == request.user
