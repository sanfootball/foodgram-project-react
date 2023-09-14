from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscription, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки админки ингредиентов."""

    empty_value_display = "-empty-"
    list_display = ("pk", "name", "measurement_unit")
    ordering = ("name",)
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки админки тегов."""

    empty_value_display = "-empty-"
    list_display = ("pk", "name", "color", "slug")
    search_fields = ("name", "slug")
    ordering = (
        "name",
        "id",
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки админки рецептов."""

    empty_value_display = "-empty-"
    list_editable = ("author",)
    list_display = (
        "pk",
        "name",
        "author",
        "text",
        "cooking_time",
        "pub_date",
    )
    list_filter = ("author", "name", "tags")
    search_fields = ("name",)
    ordering = (
        "pub_date",
        "name",
    )
    inlines = [RecipeIngredientInline]

    def num_favorites(self, obj):
        return obj.favorites.count()

    num_favorites.short_description = "Избранное"

    readonly_fields = ("num_favorites",)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Настройки соответствия игредиентов и рецептов."""

    empty_value_display = "-empty-"
    list_display = ("pk", "recipe", "ingredient", "amount")
    list_filter = ("recipe__name",)
    search_fields = ("recipe__name", "ingredient__name")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настройки админки избранного."""

    empty_value_display = "-empty-"
    list_display = (
        "pk",
        "user",
        "recipe",
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Настройки админки рецептов, которые добавлены в список покупок."""

    empty_value_display = "-empty-"
    list_display = (
        "pk",
        "user",
        "recipe",
    )


@admin.register(Subscription)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
