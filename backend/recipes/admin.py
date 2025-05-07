from django.contrib import admin
from .models import Ingredient, Recipe, Favorite, ShoppingCart


class IngredientAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления ингредиентами.

    Поля, отображаемые в списке:
    - name: Название ингредиента
    - measurement_unit: Единица измерения ингредиента

    Поля для поиска:
    - name: Поиск по названию ингредиента
    """

    list_display = ("name", "measurement_unit")
    search_fields = ("name",)


admin.site.register(Ingredient, IngredientAdmin)


class RecipeAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления рецептами.

    Поля, отображаемые в списке:
    - name: Название рецепта
    - author: Автор рецепта
    - get_favorite_count: Количество добавлений рецепта в избранное

    Поля для поиска:
    - name: Поиск по названию рецепта
    - author__username: Поиск по юзернейму автора рецепта
    """

    list_display = ("name", "author", "get_favorite_count")
    search_fields = ("name", "author__username")  # Поиск по юзернейму автора

    def get_favorite_count(self, obj):
        """
        Возвращает количество добавлений данного рецепта в избранное.

        :param obj: Экземпляр модели Recipe.
        :return: Количество добавлений в избранное.
        """
        return obj.favorited_by.count()

    get_favorite_count.short_description = "Количество добавлений в избранное"


admin.site.register(Recipe, RecipeAdmin)


class FavoriteAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления избранными рецептами.

    Поля, отображаемые в списке:
    - user: Пользователь, который добавил рецепт в избранное
    - recipe: Рецепт, добавленный в избранное
    """

    list_display = ("user", "recipe")


admin.site.register(Favorite, FavoriteAdmin)


class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления корзиной покупок.

    Поля, отображаемые в списке:
    - user: Пользователь, которому принадлежит корзина
    - recipe: Рецепт, добавленный в корзину
    """

    list_display = ("user", "recipe")


admin.site.register(ShoppingCart, ShoppingCartAdmin)
