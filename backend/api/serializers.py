import base64

from backend_foodgram.settings import PATTERN
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag)
from rest_framework import serializers, relations
from users.models import User
from rest_framework.validators import ValidationError
from django.db import transaction

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания объекта User."""

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
    """Сериализатор для модели User."""
    username = serializers.RegexField(regex=PATTERN, max_length=150)
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and Subscription.objects.filter(
            author=obj, user=user).exists()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )
        extra_kwargs = {'password': {'write_only': True}}


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для работы с картинками в формате base64."""
    def to_internal_value(self, data):
        # Проверяем, является ли переданные данные строкой base64
        if isinstance(data, str) and data.startswith('data:image'):
            # Извлекаем информацию о формате картинки
            # и само содержимое из строки base64
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')
            # Определяем расширение файла на основе информации о формате
            # И извлечь расширение файла.
            ext = format.split('/')[-1]
            # Декодируем содержимое картинки из base64
            data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
        # Применяем дефолтную логику для обработки декодированной картинки
        return super().to_internal_value(data)


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ['recipe']


class IngredientSerializer(serializers.HyperlinkedModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели RecipeIngredient."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGETSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = ('id', 'author', 'pub_date')

    def get_ingredients(self, recipe):
        return recipe.ingredients.values(
            "id",
            "name",
            "measurement_unit",
            amount=F("recipe_ingredients__amount"),
        )

    def get_is_favorited(self, obj):
        return self.extract_from_get_is_in_shopping_cart_and_is_favorited(
            Favorite, obj)

    def get_is_in_shopping_cart(self, obj):
        """Проверка - находится ли рецепт в списке покупок."""
        return self.extract_from_get_is_in_shopping_cart_and_is_favorited(
            ShoppingCart, obj)

    def extract_from_get_is_in_shopping_cart_and_is_favorited(self, arg, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return arg.objects.filter(recipe=obj, user=current_user).exists()


class RecipeCreateSerializer(RecipeGETSerializer):
    """Сериализатор для создания Recipe."""
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = IngredientCreateSerializer(many=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Мин. 1 ингредиент в рецепте!')
        return ingredients

    def validate(self, data):
        ingredients = data['ingredients']
        ingredient_ids = []
        for item in ingredients:
            ingredient_id = item['id'].id
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError(
                    'Ингредиент должен быть уникальным!')
            ingredient_ids.append(ingredient_id)
        return data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'])

    def create(self, validated_data):
        print(validated_data)
        ingredients_list = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        print("Ingredients List:", ingredients_list)
        print("Tags:", tags)
        author = self.context.get('request').user
        print("Author:", author)
        recipe = Recipe.objects.create(**validated_data)
        print("Recipe object:", recipe)
        recipe.tags.set(tags)
        print("Recipe tags:", recipe.tags.all())
        self.create_ingredients(ingredients_list, recipe)
        print("Resulting recipe:", recipe)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeGETSerializer(instance, context=context).data
