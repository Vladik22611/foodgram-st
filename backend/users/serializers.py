import base64
from djoser.serializers import UserSerializer
from rest_framework import serializers
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from .models import Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    # кастомное поле для сериализатора
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            try:
                format, imgstr = data.split(";base64,")
                ext = format.split("/")[-1]
                decoded_file = base64.b64decode(imgstr)

                # Генерация уникального имени
                file_name = f"avatar_{hash(imgstr)}.{ext}"

                return ContentFile(decoded_file, name=file_name)
            except (ValueError, AttributeError, TypeError):
                raise serializers.ValidationError("Некорректный формат base64")
        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class CustomUserSerializer(UserSerializer):
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

    # из проекта api_yatube
    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                subscriber=request.user, author=obj
            ).exists()
        return False

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None
