from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.groups.models import Session
from apps.participants.models import ParticipantProfile
from apps.accounts.models import User


class Attendance(models.Model):
    class TrustLevel(models.TextChoices):
        TRUSTED = "trusted", _("Доверенный")
        SUSPICIOUS = "suspicious", _("Подозрительный")
        BLOCKED = "blocked", _("Заблокирован")

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="attendances",
        verbose_name=_("Сессия"),
    )
    profile = models.ForeignKey(
        ParticipantProfile,
        on_delete=models.CASCADE,
        related_name="attendances",
        verbose_name=_("Профиль участника"),
    )

    fingerprint_hash = models.CharField(
        _("Хэш браузера"), max_length=64, blank=True, null=True
    )

    trust_level = models.CharField(
        _("Уровень доверия"),
        max_length=20,
        choices=TrustLevel.choices,
        default=TrustLevel.TRUSTED,
    )

    trust_score = models.PositiveSmallIntegerField(
        _("Баллы доверия"), default=100
    )

    marked_by_trainer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Отметил тренер"),
        related_name="manual_attendances",
    )

    timestamp = models.DateTimeField(
        _("Время отметки"), auto_now_add=True
    )

    class Meta:
        verbose_name = _("Отметка посещения")
        verbose_name_plural = _("Отметки посещения")
        unique_together = ("session", "profile")
        indexes = [
            models.Index(fields=["session", "profile"]),
            models.Index(fields=["fingerprint_hash"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.profile.full_name} → {self.session.date} ({self.trust_level})"
