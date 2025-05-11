from django.contrib import admin
from django.db.models import Count
from django.utils.safestring import mark_safe

from .models import Ingredient, Recipe, Favorite, ShoppingCart
from .admin_filters import HasRecipesFilter, CookingTimeFilter


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления ингредиентами.

    Поля, отображаемые в списке:
    - name: Название ингредиента
    - measurement_unit: Единица измерения ингредиента

    Поля для поиска:
    - name: Поиск по названию ингредиента
    """
    list_display = ('name', 'measurement_unit', 'recipes_usage_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit', HasRecipesFilter)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            recipes_count=Count('recipes')
        )

    @admin.display(
        description='Рецептов',
        ordering='recipes_count'
    )
    def recipes_usage_count(self, ingredient):
        return ingredient.recipes_count


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Администрирование рецептов
    """
    list_display = (
        'id', 'name', 'cooking_time', 'author',
        'favorite_count', 'ingredients_list', 'image_preview'
    )
    search_fields = ('name', 'author__username', 'ingredients__name')
    list_filter = ('author', CookingTimeFilter)
    list_select_related = ('author',)
    readonly_fields = ('image_preview',)
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _favorite_count=Count('favorited_by', distinct=True),
            _ingredients_count=Count('ingredients', distinct=True)
        ).prefetch_related('ingredients')

    @admin.display(description='В избранном', ordering='_favorite_count')
    def favorite_count(self, recipe):
        return recipe._favorite_count

    @admin.display(description='Ингредиенты')
    def ingredients_list(self, recipe):
        items = [
            f"{ing.name} - {ing.amount}{ing.measurement_unit}"
            for ing in recipe.ingredients.all()[:3]
        ]
        if recipe._ingredients_count > 3:
            items.append(f"...ещё {recipe._ingredients_count - 3}")
        return mark_safe("<br>".join(items)) if items else "-"

    @admin.display(description='Изображение')
    def image_preview(self, recipe):
        if recipe.image:
            return mark_safe(
                f'<img src="{recipe.image.url}" style="max-height: 50px; max-width: 100px;">'
            )
        return "-"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления избранными рецептами.

    Поля, отображаемые в списке:
    - user: Пользователь, который добавил рецепт в избранное
    - recipe: Рецепт, добавленный в избранное
    """

    list_display = ("user", "recipe")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления корзиной покупок.

    Поля, отображаемые в списке:
    - user: Пользователь, которому принадлежит корзина
    - recipe: Рецепт, добавленный в корзину
    """

    list_display = ("user", "recipe")
