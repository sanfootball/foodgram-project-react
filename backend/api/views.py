from http.client import NOT_FOUND

from api.paginations import CustomPagination
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .permissions import AuthorOrReadOnly
from .serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                          Limit_field_RecipeSerializer, RecipeCreateSerializer,
                          RecipeGETSerializer, ShoppingCartRecipeSerializer,
                          SubscriptionsSerializer, TagSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Вьюсет для кастомной модели пользователей."""
    pagination_class = CustomPagination

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)

    @action(methods=["GET"], detail=False,
            url_path='subscriptions',
            url_name='subscriptions',
            permission_classes=(IsAuthenticated,),
            serializer_class=SubscriptionsSerializer)
    def subscriptions(self, request):
        """Метод для получения списка подписок."""
        user = request.user
        paginated_queryset = self.paginate_queryset(
            Subscription.objects.filter(user=user))
        serializer = SubscriptionsSerializer(
            paginated_queryset, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        url_path=r'(?P<id>\d+)/subscribe',
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, *args, **kwargs):
        '''Подписка и отписка от авторов.'''
        user = request.user
        author = get_object_or_404(User, id=kwargs.get('id'))
        check_subscription = Subscription.objects.filter(
            user=user,
            author=author,
        ).exists()
        if request.method == 'POST':
            if author.id == user.id:
                return Response(
                    {'errors': 'так не пойдет, подписаться на себя нельзя!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if check_subscription:
                return Response(
                    {'errors': 'так не пойдет, ты уже подписался на автора'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            author_sub = Subscription.objects.create(
                user=user,
                author=author,
            )
            serializer = SubscriptionsSerializer(
                author_sub,
                context={
                    'request': request,
                },
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if check_subscription:
                Subscription.objects.filter(
                    user=user,
                    author=author,
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'так не пойдет, ты не подписывался на автора'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для модели Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для модели Ingredient."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filterset_class = IngredientFilter
    search_fields = ('name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipe."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeGETSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_favorited not in ('0', '1'):
            is_favorited = None
        if is_in_shopping_cart not in ('0', '1'):
            is_in_shopping_cart = None

        if self.request.user.is_authenticated:
            if is_favorited == '1':
                queryset = queryset.filter(favorites__user=self.request.user)
            if is_in_shopping_cart == '1':
                queryset = queryset.filter(
                    shopping_cart__user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGETSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['POST', 'DELETE'],
            serializer_class=FavoriteRecipeSerializer,
            permission_classes=[IsAuthenticated, ],
            url_path='favorite')
    def favorite(self, request, **kwargs):
        """Добавление/удаление рецепта в/из избранное(ого)."""
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        if request.method == 'POST':
            serializer = FavoriteRecipeSerializer(
                data={'user': request.user.id, 'recipe': recipe.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            favorite_serializer = Limit_field_RecipeSerializer(recipe)
            return Response(
                favorite_serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            try:
                favorite_recipe = get_object_or_404(
                    Favorite, user=request.user, recipe=recipe)
                favorite_recipe.delete()
                return Response(
                    'Рецепт удален из избранного',
                    status=status.HTTP_204_NO_CONTENT)
            except Favorite.DoesNotExist:
                return Response(
                    {'status': 'Рецепта нет в избранном'},
                    status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'],
            serializer_class=ShoppingCartRecipeSerializer,
            permission_classes=[IsAuthenticated, ],
            url_path='shopping_cart')
    def shopping_cart(self, request, **kwargs):
        """Добавление/удаление рецепта в/из список(ка) покупок."""
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        if request.method == 'POST':
            serializer = ShoppingCartRecipeSerializer(
                data={'user': request.user.id, 'recipe': recipe.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            shopping_cart_serializer = Limit_field_RecipeSerializer(recipe)
            return Response(
                shopping_cart_serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            try:
                shopping_cart_recipe = get_object_or_404(
                    ShoppingCart, user=request.user, recipe=recipe)
                shopping_cart_recipe.delete()
                return Response(
                    'Рецепт удален из списка покупок',
                    status=status.HTTP_204_NO_CONTENT)
            except ShoppingCart.DoesNotExist:
                return Response(
                    {'status': 'Рецепта нет в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        user = self.request.user
        filename = f'{user.username}_shopping_list.txt'
        ingredients_cart = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=self.request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(
            amount=Sum('amount')).order_by('-amount')

        shopping_list_text = [f'Список покупок пользователя: {user.username}']
        for ingredient in ingredients_cart:
            shopping_item = (
                f"{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) "
                f"— {ingredient['amount']}")
            shopping_list_text.append(shopping_item)
        shopping_list_text = '\n'.join(shopping_list_text)
        response = HttpResponse(shopping_list_text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
