from django.contrib.auth.models import AbstractUser
from django.db import models


from posts import validators


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        verbose_name="Email",
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        verbose_name="Логин",
        validators=(validators.validate_username, ),
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name="Имя",
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name="Фамилия",
    )
    password = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name="Пароль",
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        ordering = ("id",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
