import base64
from rest_framework.decorators import action
from django.db.models import Prefetch
from rest_framework import viewsets, filters, status, serializers
from django.shortcuts import redirect, get_object_or_404
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse


from .models import Recipe, Ingredient, IngredientInRecipe, ShoppingCart, Favorite
from .serializers import (
    RecipeSerializer,
    IngredientSerializer,
)
from .paginators import CustomPagination
from .permissions import RecipePermission

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    # Определим, что значение параметра search должно быть началом искомой строки
    search_fields = ("^name",)



class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    permission_classes = [RecipePermission]

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user
        params = self.request.query_params

        # Фильтрация по автору
        if author_id := params.get("author"):
            author = get_object_or_404(User, id=author_id)
            queryset = queryset.filter(author=author)

        # Фильтрация по избранному (только для авторизованных)
        if params.get("is_favorited") == "1":
            if user.is_authenticated:
                queryset = queryset.filter(favorited_by__user=user)
    

        # Фильтрация по списку покупок (только для авторизованных)
        if params.get("is_in_shopping_cart") == "1":
            if user.is_authenticated:
                queryset = queryset.filter(shoppingcart__user=user)
            

        # Оптимизированный prefetch для ингредиентов
        prefetch = Prefetch(
            "ingredients_in_recipe",
            queryset=IngredientInRecipe.objects.select_related("ingredient"),
        )

        return queryset.select_related("author").prefetch_related(prefetch).distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user

        if user.is_authenticated:
            # Одним запросом получаем все ID избранных рецептов
            context["user_favorites"] = set(
                Favorite.objects.filter(user=user).values_list("recipe_id", flat=True)
            )

            # Одним запросом получаем все ID рецептов в корзине
            context["user_cart_items"] = set(
                ShoppingCart.objects.filter(user=user).values_list(
                    "recipe_id", flat=True
                )
            )

        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # На случай других ошибок (например, 404 при get_object_or_404)
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        code = base64.urlsafe_b64encode(str(recipe.id).encode()).decode().rstrip("=")
        return Response(
            {"short-link": f"{request.build_absolute_uri('/')}foodgram/{code}"}
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
        url_path="favorite",
    )
    def favorite_action(self, request, pk=None):
        """Добавление/удаление рецепта из избранного."""
        return self._handle_recipe_action(
            request,
            model=Favorite,
            errors_already_exists="Рецепт уже в избранном",
            errors_not_exists="Рецепта нет в избранном",
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
        url_path="shopping_cart",
    )
    def shopping_cart_action(self, request, pk=None):
        """Добавление/удаление рецепта из списка покупок."""
        return self._handle_recipe_action(
            request,
            model=ShoppingCart,
            errors_already_exists="Рецепт уже в списке покупок",
            errors_not_exists="Рецепта нет в списке покупок",
        )

    def _handle_recipe_action(
        self, request, model, errors_already_exists, errors_not_exists
    ):
        """Общая логика для добавления/удаления рецепта."""
        recipe = self.get_object()
        user = request.user

        if request.method == "POST":
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"errors": errors_already_exists},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            model.objects.create(user=user, recipe=recipe)
            return Response(
                {
                    "id": recipe.id,
                    "name": recipe.name,
                    "image": (
                        request.build_absolute_uri(recipe.image.url)
                        if recipe.image
                        else None
                    ),
                    "cooking_time": recipe.cooking_time,
                },
                status=status.HTTP_201_CREATED,
            )

        elif request.method == "DELETE":
            obj = model.objects.filter(user=user, recipe=recipe).first()
            if not obj:
                return Response(
                    {"errors": errors_not_exists},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="download_shopping_cart",
    )
    def download_shopping_cart(self, request):
        """
        Скачать список покупок в формате TXT.
        Доступно только авторизованным пользователям.
        """
        user = request.user

        # Получаем все рецепты в корзине пользователя
        cart_recipes = Recipe.objects.filter(shoppingcart__user=user).prefetch_related(
            "ingredients_in_recipe__ingredient"
        )

        # Собираем ингредиенты с суммарным количеством
        ingredients = {}
        for recipe in cart_recipes:
            for ingredient_in_recipe in recipe.ingredients_in_recipe.all():
                ingredient = ingredient_in_recipe.ingredient
                amount = ingredient_in_recipe.amount

                if ingredient.id not in ingredients:
                    ingredients[ingredient.id] = {
                        "name": ingredient.name,
                        "measurement_unit": ingredient.measurement_unit,
                        "amount": 0,
                    }
                ingredients[ingredient.id]["amount"] += amount

        # Формируем текстовый файл
        content = "Список покупок:\n\n"
        for ingredient in ingredients.values():
            content += (
                f"{ingredient['name']} "
                f"({ingredient['measurement_unit']}) - "
                f"{ingredient['amount']}\n"
            )

        # Создаем HTTP-ответ с файлом
        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = 'attachment; filename="shopping_list.txt"'
        return response


def redirect_short_link(request, code):
    try:
        padding = len(code) % 4
        if padding:
            code += "=" * (4 - padding)

        recipe_id = int(base64.urlsafe_b64decode(code.encode()).decode())
        recipe = Recipe.objects.get(pk=recipe_id)
        return redirect(f"/api/recipes/{recipe.id}/")
    except (ValueError, Recipe.DoesNotExist):
        return Response({"error": "Not found"}, status=404)
