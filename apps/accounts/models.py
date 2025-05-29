import secrets
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Кастомная модель пользователя с ролями, отчеством
    """
    class Role(models.TextChoices):
        TRAINER = "trainer", _("Тренер")
        ADMIN = "admin", _("Администратор")

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TRAINER,
        verbose_name=_("Роль"),
    )

    middle_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name=_("Отчество"),
    )

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        ordering = ["-date_joined"]

    def __str__(self):
        parts = filter(None, [self.last_name, self.first_name, self.middle_name])
        return " ".join(parts).strip()

    @staticmethod
    def generate_nonce(length=16):
        """Генерация безопасного nonce (для аутентификации, QR и т.п.)"""
        return secrets.token_urlsafe(length)
