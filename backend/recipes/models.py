from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Ingredient(models.Model):
    """
    Модель для представления ингредиента.

    Поля:
    - name: Название ингредиента (максимум 128 символов)
    - measurement_unit: Единица измерения ингредиента (максимум 64 символа)
    """

    name = models.CharField(max_length=128)
    measurement_unit = models.CharField(max_length=64)

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

    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="recipes")
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to="recipes/img/")
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)
    ingredients = models.ManyToManyField(
        Ingredient, through="IngredientInRecipe", related_name="recipes"
    )

    class Meta:
        ordering = ["-pub_date"]


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
        Recipe, on_delete=models.CASCADE, related_name="ingredients_in_recipe"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_ingredient_in_recipe"
            )
        ]


class Favorite(models.Model):
    """
     Модель для представления избранных рецептов пользователя.

     Поля:
     - user: Пользователь, который добавил рецепт в избранное (ссылка на User)
     - recipe: Рецепт, добавленный в избранное (ссылка на Recipe)

    Метаданные:
    - constraints: Уникальность на сочетание user и recipe.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="favorites")
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorited_by"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe"],
                                    name="unique_favorite")
        ]


class ShoppingCart(models.Model):
    """
    Модель для представления корзины покупок пользователя.

    Поля:
    - user: Пользователь, которому принадлежит корзина (ссылка на User)
    - recipe: Рецепт, добавленный в корзину (ссылка на Recipe)

    Метаданные:
    - constraints: Уникальное ограничение на сочетание user и recipe.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_cart"
            )
        ]
