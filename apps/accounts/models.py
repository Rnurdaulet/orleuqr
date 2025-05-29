import secrets
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Кастомная модель пользователя с ролями, отчеством
    """
    middlename = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name=_("Отчество")
    )

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        ordering = ["-date_joined"]

    @staticmethod
    def generate_nonce(length=16):
        """Генерация безопасного nonce"""
        return secrets.token_urlsafe(length)


    def __str__(self):
        full_name = f"{self.last_name} {self.first_name}"
        if self.middlename:
            full_name += f" {self.middlename}"
        return f"{full_name.strip()}"

