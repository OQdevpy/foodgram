from django.contrib.auth import get_user_model
from django.utils.timezone import now
from posts.models import Subscribe

from djoser import views

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny  # IsAuthenticated
from rest_framework.response import Response

# from users import serializers
# import actions
# from djoser import utils
# from djoser.conf import settings

from api.serializers import SubscribeCreateSerializer, UserCreateSerializer  # UserSerializer


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        pass



class AuthViewSet(views.UserViewSet):

    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action == 'login':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'register':
            return UserCreateSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['post'], permission_classes=[AllowAny],)
    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(is_active=True)
        data = serializer.data
        return Response(
            data=data, status=status.HTTP_200_OK
        )

    @action(["post"], detail=False, permission_classes=[AllowAny],)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.user.set_password(serializer.data["new_password"])
        if hasattr(serializer.user, "last_login"):
            serializer.user.last_login = now()
        serializer.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
