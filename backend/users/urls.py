from django.urls import path, include
from .views import AvatarAPIView, SubscriptionViewSet
from rest_framework import routers 

router = routers.DefaultRouter()

router.register("users", SubscriptionViewSet, basename='subscribe-user')

urlpatterns = [
    path("users/me/avatar/", AvatarAPIView.as_view(), name="user-avatar"),
    path("", include(router.urls)),
    path("", include("djoser.urls")),  # Работа с пользователями
    path("auth/", include("djoser.urls.authtoken")),  # Работа с токенами
]
