from colorfield.fields import ColorField

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from posts import validators

User = get_user_model()

MIN_TIME = 1
MAX_TIME = 120


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Название тега",
        validators=(validators.validate_username, ),
    )
    color = ColorField()
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="Слаг",
        validators=(validators.validate_slug, )
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название",
        validators=(validators.validate_username, ),
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Мера измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиент',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Tег',
    )
    image = models.ImageField(
        blank=True,
        null=True,
        verbose_name='Картинка',
        upload_to='recipe/',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )
    text = models.TextField(
        verbose_name='Описание',
        max_length=500,
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_TIME,
                                      message="Минимальное время - 1"),
                    MaxValueValidator(MAX_TIME,
                                      message="Максимальное время - 120")],
        verbose_name='Время приготовления (в минутах)'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )

    class Meta:
        ordering = ['user']
        verbose_name = ('Избранный рецепт')
        verbose_name_plural = ('Избранные рецепты')

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у пользователя {self.user}.'


class IngredientsRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe',
    )
    amount = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return self.ingredient


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )


class ShoppingCard(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',

    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = 'Список покупок'

    def __str__(self):
        return (f'Пользователь {self.user} добавил в '
                f'список покупок рецепт {self.recipe}.')


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'Пользователь {self.user} подписан на автора {self.author}.'
