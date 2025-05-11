import base64
from djoser.serializers import UserSerializer
from rest_framework import serializers
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model

from .models import Subscription
from recipes.models import Recipe
from recipes.base_serializers import ShortRecipeSerializer

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """
    Кастомное поле для сериализатора, для изображения в формате base64.
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            try:
                format, imgstr = data.split(";base64,")
                ext = format.split("/")[-1]
                decoded_file = base64.b64decode(imgstr)

                # Генерация уникального имени файла
                file_name = f"avatar_{hash(imgstr)}.{ext}"

                return ContentFile(decoded_file, name=file_name)
            except (ValueError, AttributeError, TypeError):
                raise serializers.ValidationError("Некорректный формат base64")
        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    """
    Сериализатор для загрузки аватара пользователя.
    """

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ("avatar",)


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор для пользователя с дополнительной
    информацией о подписках и аватаре.
    """

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )
        read_only_fields = ("username",)

    def get_is_subscribed(self, obj):
        """
        Проверяет, подписан ли текущий пользователь на данного пользователя.
        """
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                subscriber=request.user, author=obj
            ).exists()
        return False

    def get_avatar(self, obj):
        """
        Возвращает URL аватара пользователя.
        """
        if obj.avatar:
            return obj.avatar.url
        return None


class SubscriptionSerializer(CustomUserSerializer):
    """
    Сериализатор для подписок с дополнительной информацией о рецептах автора.
    """

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ("recipes", "recipes_count")

    def get_recipes(self, obj):
        """
        Возвращает рецепты автора с возможностью ограничения количества.
        """

        request = self.context.get("request")
        recipes = Recipe.objects.filter(author=obj)

        # Ограничение количества рецептов по параметру запроса
        recipes_limit = request.query_params.get("recipes_limit") if request else None
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[: int(recipes_limit)]

        return ShortRecipeSerializer(
            recipes, many=True, context={"request": request}
        ).data

    def get_recipes_count(self, obj):
        """
        Возвращает общее количество рецептов автора.
        """

        return obj.recipes.count()
