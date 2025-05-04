from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import AvatarSerializer

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
            return Response({"avatar": user.avatar.url}, 
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        if not user.avatar:
            return Response(
                {"detail": "Аватар не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
