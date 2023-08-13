from users.models import User
from rest_framework import serializers
from backend_foodgram.settings import PATTERN

from djoser.serializers import UserCreateSerializer, UserSerializer


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания объекта класса User."""

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserSerializer(UserSerializer):
    username = serializers.RegexField(regex=PATTERN, max_length=150)
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, User):
        return User.username == 'is_subscribed'

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )
        extra_kwargs = {'password': {'write_only': True}}
