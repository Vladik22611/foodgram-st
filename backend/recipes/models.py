from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Ingredient(models.Model):
    """
    Модель для представления ингредиента.

    Поля:
    - name: Название ингредиента (максимум 128 символов)
    - measurement_unit: Единица измерения ингредиента (максимум 64 символа)
    """

    name = models.CharField(
        max_length=128, verbose_name="Название ингредиента", unique=True
    )
    measurement_unit = models.CharField(max_length=64,
                                        verbose_name="Единица измерения")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"], name="unique_ingredient"
            )
        ]
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    """
    Модель для представления рецепта.

    Поля:
    - author: Автор рецепта (ссылка на пользователя)
    - name: Название рецепта (максимум 256 символов)
    - image: Изображение рецепта
    - text: Описание рецепта
    - cooking_time: Время приготовления в минутах (положительное целое число)
    - pub_date: Дата и время публикации рецепта
    - ingredients: Ингредиенты, используемые в рецепте
    (связь многие-ко-многим с Ingredient через IngredientInRecipe)

    Метаданные:
    - ordering: Сортировка по дате публикации (по убыванию)
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
    )
    name = models.CharField(max_length=256, verbose_name="Название рецепта")
    image = models.ImageField(
        upload_to="recipes/img/", verbose_name="Изображение блюда"
    )
    text = models.TextField(verbose_name="Описание рецепта")
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления (минуты)",
        validators=[
            MinValueValidator(
                1, message="Время приготовления не может быть меньше 1")]
    )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name="Дата публикации")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientInRecipe",
        related_name="recipes",
        verbose_name="Ингредиенты",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)


class IngredientInRecipe(models.Model):
    """
    Модель для представления связи между рецептом и ингредиентом.

    Поля:
    - recipe: Рецепт, к которому относится ингредиент (ссылка на Recipe)
    - ingredient: Ингредиент, используемый в рецепте (ссылка на Ingredient)
    - amount: Количество ингредиента, необходимое для рецепта
    (положительное целое число)

    Метаданные:
    - constraints: Уникальность сочетания recipe и ingredient.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients_in_recipe",
        verbose_name="Рецепт"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_occurrences',
        verbose_name="Ингредиент"
    )
    amount = models.PositiveIntegerField(
        verbose_name="Количество",
        validators=[
            MinValueValidator(
                1,
                message="Количество не может быть меньше 1"
            )
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_ingredient_in_recipe"
            )
        ]
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"

    def __str__(self):
        return f"{self.ingredient.name} - {self.amount} {self.ingredient.measurement_unit}"


class UserRecipeRelation(models.Model):
    """
    Абстрактная модель для связи пользователь-рецепт
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_relations',
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s_relations',
        verbose_name="Рецепт"
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_%(class)s'
            )
        ]

    def __str__(self):
        return f"{self.user.username} → {self.recipe.name}"


class Favorite(UserRecipeRelation):
    """
    Модель для избранных рецептов пользователя
    """
    class Meta(UserRecipeRelation.Meta):
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"


class ShoppingCart(UserRecipeRelation):
    """
    Модель для рецептов в корзине покупок
    """
    class Meta(UserRecipeRelation.Meta):
        verbose_name = "Рецепт в списке покупок"
        verbose_name_plural = "Рецепты в списке покупок"
