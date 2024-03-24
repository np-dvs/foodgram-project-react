from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from foodgram.constants import MAX_LENGTH_TAG, MAX_VALUE_AND_LENGTH
from users.models import User


class Tag(models.Model):
    """Модель Тег."""

    name = models.CharField(max_length=MAX_LENGTH_TAG,
                            verbose_name='Название')
    color = ColorField(format='hex',
                       unique=True,
                       verbose_name='Цвет')
    slug = models.SlugField(max_length=MAX_LENGTH_TAG,
                            unique=True,
                            blank=True,
                            verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Модель Ингредиент."""

    name = models.CharField(max_length=MAX_VALUE_AND_LENGTH,
                            verbose_name='Ингредиент')
    measurement_unit = models.CharField(max_length=MAX_VALUE_AND_LENGTH,
                                        verbose_name='Единица измерения')

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('name', 'measurement_unit'),
                                    name='unique_name_and_measurement_unit'),
        )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """Модель Рецепт."""

    name = models.CharField(max_length=MAX_VALUE_AND_LENGTH,
                            verbose_name='Название')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор')
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         related_name='recipes',
                                         verbose_name='ингредиенты')
    slug = models.SlugField(max_length=MAX_VALUE_AND_LENGTH,
                            verbose_name='Слаг',
                            blank=True)
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    image = models.ImageField(upload_to='foodgram_backend/',
                              verbose_name='Фото')
    tags = models.ManyToManyField(Tag,
                                  related_name='recipes',
                                  verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(validators=[
        MinValueValidator(1, message='Слишком быстро!'
                          '(минимальное значение = 1)')],
        verbose_name='Время приготовления')

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class IngredientInRecipe(models.Model):
    """
    М2М.

    Модель для М2М связи ингредиента
    и рецепта.
    """

    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='ingredient_in_recipe')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='ingredient_in_recipe')
    amount = models.PositiveSmallIntegerField(validators=[MinValueValidator(
        1, message='О нет, вы не добавили количество!:(')],
    )

    class Meta:
        constraints = (models.UniqueConstraint(
            fields=('recipe', 'ingredient'),
            name='unique_recipe_and_ingredient'
        ),)
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self) -> str:
        return f'{self.ingredient} in {self.recipe}'


class FavoriteShoppingCartModel(models.Model):
    """Базовая модель для Корзины покупок и Избранного."""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')

    class Meta:
        abstract = True


class Favourites(FavoriteShoppingCartModel):
    """Модель Избранное."""

    class Meta(FavoriteShoppingCartModel.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(FavoriteShoppingCartModel):
    """Модель Корзина покупок."""

    class Meta(FavoriteShoppingCartModel.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'


class Subscribe(models.Model):
    """Модель Подписки."""

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['id']

        def __str__(self) -> str:
            return f'Подпичик - {self.user} подписан на {self.author}'
