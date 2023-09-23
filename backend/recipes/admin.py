from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscription, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки админки ингредиентов."""

    empty_value_display = '-empty-'
    list_display = ('pk', 'name', 'measurement_unit')
    ordering = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки админки тегов."""

    empty_value_display = '-empty-'
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')
    ordering = ('name', 'id',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки админки рецептов."""

    empty_value_display = '-empty-'
    list_editable = ('author',)
    list_display = ('pk', 'name', 'author', 'text', 'cooking_time',
                    'display_image', 'pub_date')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name',)
    ordering = ('pub_date', 'name',)
    inlines = [RecipeIngredientInline]

    def display_image(self, obj):
        return format_html(
            f'<img src="{obj.image.url}" '
            f'style="max-height: 100px; max-width: 100px;" />')

    display_image.short_description = 'Image'

    def num_favorites(self, obj):
        """Подсчитывает количество избранных рецептов
        для отображения в админке."""
        return obj.favorites.count()

    num_favorites.short_description = 'Избранное'

    fields = ('name', 'text', 'author', 'cooking_time', 'tags', 'image',
              'preview', 'num_favorites',)
    readonly_fields = ('preview', 'num_favorites',)

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" '
                         f'style="max-height: 200px; max-width: 200px;"/>')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Настройки соответствия игредиентов и рецептов."""

    empty_value_display = '-empty-'
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    list_filter = ('recipe__name',)
    search_fields = ('recipe__name', 'ingredient__name')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настройки админки избранного."""

    empty_value_display = '-empty-'
    list_display = ('pk', 'user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Настройки админки рецептов, которые добавлены в список покупок."""

    empty_value_display = '-empty-'
    list_display = ('pk', 'user', 'recipe')


@admin.register(Subscription)
class FollowAdmin(admin.ModelAdmin):
    """Конфигурация админки подписок."""
    list_display = ('user', 'author')
