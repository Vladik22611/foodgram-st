from rest_framework import serializers
from .models import Recipe, IngredientInRecipe, Ingredient
from users.serializers import Base64ImageField, CustomUserSerializer


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    ingredients = serializers.SerializerMethodField()  # Для вывода
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(
        min_value=1,
        error_messages={
            "min_value": "Время приготовления должно быть не менее 1 минуты"
        },
    )

    class Meta:
        model = Recipe
        fields = [
            "id",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        ]
        read_only_fields = ["author", "pub_date"]

    def get_ingredients(self, obj):
        """Формат вывода ингредиентов"""
        return [
            {
                "id": ing.ingredient.id,
                "name": ing.ingredient.name,
                "measurement_unit": ing.ingredient.measurement_unit,
                "amount": ing.amount,
            }
            for ing in
            obj.ingredients_in_recipe.select_related("ingredient").all()
        ]

    def to_internal_value(self, data):
        """Обработка входящих данных"""
        data = data.copy()
        ingredients_data = data.pop("ingredients", None)

        validated_data = super().to_internal_value(data)

        if ingredients_data is None:
            raise serializers.ValidationError(
                {"ingredients": ["Это поле обязательно."]}
            )

        if not isinstance(ingredients_data, list) or not ingredients_data:
            raise serializers.ValidationError(
                {"ingredients": ["Добавьте хотя бы один ингредиент"]}
            )

        validated_data["ingredients"] = ingredients_data
        return validated_data

    def validate(self, data):
        ingredients = data.get("ingredients", [])

        # Проверка на пустой список
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": ["Добавьте хотя бы один ингредиент"]}
            )

        # Проверка на дубликаты
        ingredient_ids = [ing["id"] for ing in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {"ingredients": ["Ингредиенты не должны повторяться"]}
            )

        # Проверка существования ингредиентов
        existing_ids = set(
            Ingredient.objects.filter(id__in=ingredient_ids).values_list(
                "id", flat=True
            )
        )

        missing_ids = set(ingredient_ids) - existing_ids
        if missing_ids:
            raise serializers.ValidationError(
                {
                    "ingredients": [
                        f"Ингредиент с id {id} не существует" for id in
                        missing_ids
                    ]
                }
            )

        # Проверка структуры каждого ингредиента
        for ing in ingredients:
            if not isinstance(ing, dict):
                raise serializers.ValidationError(
                    {"ingredients": ["Каждый ингредиент должен быть объектом"]}
                )
            if "id" not in ing or "amount" not in ing:
                raise serializers.ValidationError(
                    {
                        "ingredients": [
                            "Каждый ингредиент должен" "содержать id и amount"
                        ]
                    }
                )
            if int(ing["amount"]) <= 0:
                raise serializers.ValidationError(
                    {
                        "ingredients": [
                            "Количество должно быть положительным целым числом"
                        ]
                    }
                )

        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients_data:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient["id"],
                amount=int(ingredient["amount"]),
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", None)

        if ingredients_data is not None:
            instance.ingredients_in_recipe.all().delete()
            for ingredient in ingredients_data:
                IngredientInRecipe.objects.create(
                    recipe=instance,
                    ingredient_id=ingredient["id"],
                    amount=int(ingredient["amount"]),
                )

        return super().update(instance, validated_data)

    def get_is_favorited(self, obj):
        favorites = self.context.get("user_favorites", set())
        return obj.id in favorites

    def get_is_in_shopping_cart(self, obj):
        cart_items = self.context.get("user_cart_items", set())
        return obj.id in cart_items


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]
