from django.contrib import admin
from .models import (
    Recipe,
    Ingredient,
    Tag,
    RecipeIngredient,
    Favorite,
    ShoppingCart
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Класс настройки админки ингредиентов."""

    list_display = (
        'pk',
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Класс настройки админки тегов."""

    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )
    search_fields = ('name', 'slug')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Класс настройки админки рецептов."""

    list_display = (
        'pk',
        'name',
        'author',
        'text',
        'cooking_time',
        'image',
        'pub_date',
    )
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name',)
    inlines = [RecipeIngredientInline]

    def num_favorites(self, obj):
        return obj.favorites.count()
    num_favorites.short_description = 'Избранное'

    readonly_fields = ('num_favorites',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Класс настройки соответствия игредиентов и рецептов."""

    list_display = (
        'pk',
        'recipe',
        'ingredient',
        'amount'
    )
    list_filter = ('recipe__name',)
    search_fields = ('recipe__name', 'ingredient__name')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Класс настройки админки избранного."""

    list_display = (
        'pk',
        'user',
        'recipe',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Класс настройки админки рецептов, которые добавлены в список покупок."""

    list_display = (
        'pk',
        'user',
        'recipe',
    )
