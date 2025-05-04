from django.urls import path, include
from .views import AvatarAPIView

urlpatterns = [
    path("users/me/avatar/", AvatarAPIView.as_view(), name="user-avatar"),
    path("", include("djoser.urls")),  # Работа с пользователями
    path("auth/", include("djoser.urls.authtoken")),  # Работа с токенами
]
