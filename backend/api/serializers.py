import base64

from backend_foodgram.settings import PATTERN
from django.core.files.base import ContentFile
from django.db.models import F
from django.forms import ValidationError
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import User


class CustomUserSerializer(UserSerializer, UserCreateSerializer):
    """Сериализатор для модели User."""
    username = serializers.RegexField(regex=PATTERN, max_length=150)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password',
            'is_subscribed')
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.subscriber.filter(author=obj).exists())


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для работы с картинками в формате base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
        return super().to_internal_value(data)


class IngredientSerializer(serializers.HyperlinkedModelSerializer):
    """Сериализатор для модели Ingredient."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели RecipeIngredient."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиента в рецепте."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGETSerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецепта."""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = serializers.ReadOnlyField(source='image.url')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('id', 'author', 'pub_date')

    def get_ingredients(self, recipe):
        """Получает информацию об ингредиентах для рецепта."""
        return recipe.ingredients.values(
            "id", "name", "measurement_unit",
            amount=F("recipe_ingredients__amount"))

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное."""
        return self.check_user_relation_to_object(
            Favorite, obj)

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, добавлен ли рецепт в список покупок."""
        return self.check_user_relation_to_object(
            ShoppingCart, obj)

    def check_user_relation_to_object(self, arg, obj):
        """Проверяет отношение текущего пользователя к объекту (рецепту)
        в контексте избранного или списка покупок."""
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return arg.objects.filter(recipe=obj, user=current_user).exists()


class RecipeCreateSerializer(RecipeGETSerializer):
    """Сериализатор для создания рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = IngredientCreateSerializer(many=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def validate(self, data):
        """Проверяет валидность данных при создании рецепта."""
        ingredients = data['ingredients']
        ingredient_ids = []
        for item in ingredients:
            ingredient_id = item['id'].id
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError(
                    'Ингредиент должен быть уникальным!')
            ingredient_ids.append(ingredient_id)
        if not ingredients:
            raise serializers.ValidationError(
                'Минимум 1 ингредиент должен быть в рецепте!')
        return data

    def create_ingredients(self, ingredients, recipe):
        """Создает связи между рецептом и ингредиентами."""
        for ingredient in ingredients:
            RecipeIngredient.objects.get_or_create(
                recipe=recipe, ingredient=ingredient['id'],
                amount=ingredient['amount'])

    def create(self, validated_data):
        """Создает новый рецепт."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        instance.tags.set(tags)
        self.create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, recipe):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeGETSerializer(recipe, context=context).data


class Limit_field_RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для представления рецептов с неполным набором
    полей в списке покупок, списке избранных рецептов и подписках."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели избранного Favorite."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(), fields=('user', 'recipe'),
                message='Рецепт уже в списке избранных')
        ]


class ShoppingCartRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели списка покупок ShoppingCart."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(), fields=('user', 'recipe'),
                message='Рецепт уже есть в списке покупок')
        ]


class SubscriptionsSerializer(UserSerializer):
    '''Сериалайзер для работы с подписками.'''
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'recipes',
            'is_subscribed', 'recipes_count')
        read_only_fields = [
            'email', 'id', 'username', 'first_name', 'last_name', 'recipes',
            'is_subscribed', 'recipes_count']

    def validate(self, data):
        """Проверка корректности подписок у пользователя."""
        user = self.context.get('request').user
        author = self.instance
        if self.context.get('request').method == 'POST':
            if Subscription.objects.filter(
                    user=user, author=author).exists():
                raise ValidationError('Вы уже подписаны на этого автора')
            if user == author:
                raise ValidationError('Подписаться на себя нельзя!')
            return data
        if self.context.get('request').method == 'DELETE':
            if Subscription.objects.filter(
                    user=user, author=author).exists():
                return data
            raise ValidationError('Вы не подписываны на этого автора')

    def get_is_subscribed(self, obj):
        '''Проверка подписки пользователя на автора рецепта.'''
        return True

    def get_recipes(self, obj):
        """Получение рецептов автора."""
        recipes_limit = int(self.context['request'].query_params.get(
            'recipes_limit', default=3)
        )
        recipes = obj.recipes.all()[:recipes_limit]
        serializer = Limit_field_RecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Получение количество рецептов автора."""
        return obj.recipes.count()
