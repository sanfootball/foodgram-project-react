from django.contrib.auth import get_user_model
# from django.shortcuts import get_object_or_404
# from users.models import User

from djoser.views import UserViewSet

# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework import status
# from .serializers import UserSerializer


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Для кастомной модели пользователей."""
    pass
