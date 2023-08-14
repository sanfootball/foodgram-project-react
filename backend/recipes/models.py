from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента для рецептов.
    Описывает продукты, необходимые для приготовления блюда по рецепту.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
        db_index=True
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Ед. измерения.'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, ({self.measurement_unit})'


class Tag(models.Model):
    """Модель тега для рецептов.
    Описывает метки, с помощью которых пользователи размечают публикации.
    """
    name = models.CharField(
        max_length=20,
        verbose_name='Имя тега',
        unique=True
    )
    color = models.CharField(
        max_length=10,
        verbose_name='Цвет тега',
        unique=True
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='slug',
        unique=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта.
    Описывает рецепты, которые пользователи публикуют на сервисе.
    """
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
        db_index=True
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='resipes/'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, мин'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='ингредиенты'
    )

    class Meta:
        ordering = ['-pub_date', 'name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная модель для связи рецепта и ингредиента."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        ordering = ['recipe__name']
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return f'{self.recipe}: {self.ingredient}'


class Favorite(models.Model):
    """Модель для связи избранного рецепта и пользователя."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    class Meta:
        ordering = ['recipe', 'user']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return '{self.user}: {self.recipe}'


class ShoppingCart(models.Model):
    """Модель связывает пользователя и добавленные в корзину рецепты."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )

    class Meta:
        ordering = ['recipe', 'user']
        verbose_name = 'Рецепт из списка покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return '{self.user}: {self.recipe}'
