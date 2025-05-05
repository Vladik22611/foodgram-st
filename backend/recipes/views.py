import base64
from rest_framework.decorators import action
from django.db.models import Prefetch
from rest_framework import viewsets, filters, status, serializers
from django.shortcuts import redirect, get_object_or_404
from rest_framework.response import Response
from django.contrib.auth import get_user_model


from .models import Recipe, Ingredient, ShoppingCart, Favorite, IngredientInRecipe
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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    permission_classes = [RecipePermission]

    def get_queryset(self):
        queryset = Recipe.objects.all()

        author_id = self.request.query_params.get("author")

        # Фильтрация по автору
        if author_id:
            author = get_object_or_404(User, id=author_id)
            queryset = queryset.filter(author=author)

        # Оптимизированный prefetch для ингредиентов
        prefetch = Prefetch(
            "ingredients_in_recipe",
            queryset=IngredientInRecipe.objects.select_related("ingredient"),
        )

        return queryset.select_related("author").prefetch_related(prefetch)

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
