from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    """
    Модель пользователя с расширенными полями.

    Атрибуты:
        username (str): Уникальное имя пользователя.
        email (str): Уникальный адрес электронной почты,
                     используется для входа.
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        avatar (ImageField): Аватар пользователя.
    """

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+$",
                message="Username может содержать только буквы, цифры и @.+-_",
            )
        ],
        verbose_name="Имя пользователя",
    )

    email = models.EmailField("Адрес электронной почты", unique=True,
                              max_length=254)

    first_name = models.CharField("Имя", max_length=150)

    last_name = models.CharField("Фамилия", max_length=150)

    avatar = models.ImageField(upload_to="users/avatars/",
                               null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "password"]

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        """Возвращает строковое представление имени пользователя."""
        return self.username


User = get_user_model()


class Subscription(models.Model):
    """
    Модель подписки между пользователями.

    Атрибуты:
        subscriber (FK): Пользователь, который подписывается.
        author (FK): Пользователь, на которого подписываются.
    """

    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriptions"
    )

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscribers"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["subscriber", "author"], name="unique_subscription"
            ),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F("author")),
                name="no_self_subscription",
            ),
        ]
