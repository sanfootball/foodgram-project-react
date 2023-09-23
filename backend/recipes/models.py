from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from .utils import upload_to

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента для рецептов.
    Описывает продукты, необходимые для рецепта."""

    name = models.CharField(
        max_length=200, verbose_name="Название ингредиента", db_index=True
    )
    measurement_unit = models.CharField(
        max_length=200, verbose_name="Ед. измерения."
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name}, ({self.measurement_unit})"


class Tag(models.Model):
    """Модель тега для рецептов.
    Описывает теги, с помощью которых пользователи могут
    выбрать рецепты соответствующие этому тегу."""

    name = models.CharField(
        max_length=200, verbose_name="Имя тега", unique=True
    )
    color = models.CharField(
        max_length=7, verbose_name="Цвет тега", unique=True,
        validators=[RegexValidator(
            regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
            message='Цвет должен быть в формате HEX (например, #FF0000)',
        )]
    )
    slug = models.SlugField(
        max_length=200, verbose_name="slug", unique=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта.
    Описывает рецепты, которые пользователи размещают на сайте."""

    name = models.CharField(
        verbose_name="Название рецепта", max_length=200, db_index=True
    )
    text = models.TextField(verbose_name="Описание")
    image = models.ImageField(verbose_name="Изображение", upload_to=upload_to)
    pub_date = models.DateTimeField(
        verbose_name="Дата создания", auto_now_add=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор"
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления, мин",
        validators=[MinValueValidator(1, message="Не меньше 1 мин")]
    )
    tags = models.ManyToManyField(Tag, verbose_name="Теги")
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient", verbose_name="ингредиенты"
    )

    class Meta:
        ordering = ["-pub_date", "name"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        default_related_name = "recipes"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "author"], name="unique_recipe_author"
            )
        ]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная модель для связи рецепта и ингредиента."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipe_ingredients"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name="recipe_ingredients"
    )
    amount = models.PositiveSmallIntegerField(verbose_name="Количество")

    class Meta:
        ordering = ["recipe__name"]
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        constraints = [
            models.UniqueConstraint(
                fields=["ingredient", "recipe"],
                name="unique_ingredient_recipe")
        ]

    def __str__(self):
        return f"{self.recipe}: {self.ingredient}"


class Favorite(models.Model):
    """Модель для связи избранного рецепта и пользователя."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorites"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorites"
    )

    class Meta:
        ordering = ["recipe", "user"]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные рецепты"

    def __str__(self):
        return "{self.user}: {self.recipe}"


class ShoppingCart(models.Model):
    """Модель связывает пользователя и добавленные в корзину рецепты."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="shopping_cart",
        verbose_name="рецепт"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shopping_cart",
        verbose_name="Пользователь"
    )

    class Meta:
        ordering = ["recipe", "user"]
        verbose_name = "Рецепт из списка покупок"
        verbose_name_plural = "Список покупок"

    def __str__(self):
        return "{self.user}: {self.recipe}"


class Subscription(models.Model):
    """Модель подписок на авторов рецептов."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriber",
        verbose_name="Подписчик"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscribing",
        verbose_name="Автор"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_subscribe")
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
