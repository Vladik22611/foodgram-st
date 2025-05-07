from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters, viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action


from .serializers import AvatarSerializer, SubscriptionSerializer
from .models import Subscription
from recipes.paginators import CustomPagination

User = get_user_model()


class AvatarAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvatarSerializer

    def put(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data)

        if serializer.is_valid():
            # Удаляем старый аватар
            if user.avatar:
                user.avatar.delete(save=False)

            serializer.save()
            return Response({"avatar": user.avatar.url}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        if not user.avatar:
            return Response(
                {"detail": "Аватар не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


# основа взята из https://github.com/Vladik22611/api_final_yatube/blob/master/yatube_api/api/views.py
class SubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination  # Используем наш кастомный пагинатор

    @action(detail=False, methods=["get"])
    def subscriptions(self, request):
        """Список подписок текущего пользователя"""
        queryset = User.objects.filter(
            subscribers__subscriber=request.user
        ).order_by('id')
        
        # Применяем пагинацию
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = SubscriptionSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return paginator.get_paginated_response(serializer.data) 
        
        subscribed_authors = User.objects.filter(subscribers__subscriber=request.user)
        serializer = SubscriptionSerializer(
            subscribed_authors, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["post", "delete"])
    def subscribe(self, request, pk=None):
        """Подписаться/отписаться от пользователя"""
        author = get_object_or_404(User, pk=pk)

        if request.method == "POST":
            # Проверка подписки на себя
            if request.user == author:
                return Response(
                    {"error": "Нельзя подписаться на себя"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Проверка существующей подписки
            if Subscription.objects.filter(
                subscriber=request.user, author=author
            ).exists():
                return Response(
                    {"error": "Вы уже подписаны на этого пользователя"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Subscription.objects.create(subscriber=request.user, author=author)

            serializer = SubscriptionSerializer(author, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            subscription = Subscription.objects.filter(
                subscriber=request.user, author=author
            ).first()

            if not subscription:
                return Response(
                    {"error": "Вы не подписаны на этого пользователя"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
