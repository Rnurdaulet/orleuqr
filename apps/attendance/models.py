from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.groups.models import Session
from apps.participants.models import PersonProfile
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
        PersonProfile,
        on_delete=models.CASCADE,
        related_name="attendances",
        verbose_name=_("Профиль участника"),
    )

    # ⏱️ Время входа и выхода
    arrived_at = models.DateTimeField(_("Время прихода"), null=True, blank=True)
    left_at = models.DateTimeField(_("Время ухода"), null=True, blank=True)

    # 🧠 Идентификация по браузеру
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

    # 🧍 Отметка вручную тренером
    marked_by_trainer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Отметил тренер"),
        related_name="manual_attendances",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Отметка посещения")
        verbose_name_plural = _("Отметки посещения")
        unique_together = ("session", "profile")
        indexes = [
            models.Index(fields=["session", "profile"]),
            models.Index(fields=["fingerprint_hash"]),
        ]
        ordering = ["-arrived_at"]

    def __str__(self):
        return f"{self.profile.full_name} → {self.session.date} ({self.trust_level})"

    def is_present(self):
        return bool(self.arrived_at)

    def is_left(self):
        return bool(self.left_at)


class TrustLog(models.Model):
    fingerprint = models.ForeignKey(
        "participants.BrowserFingerprint",
        on_delete=models.CASCADE,
        related_name="trust_logs",
        verbose_name=_("Отпечаток"),
        null=True,
        blank=True,
    )
    attendance = models.ForeignKey(
        "attendance.Attendance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Связанная отметка"),
    )
    reason = models.CharField(_("Причина"), max_length=255)
    delta = models.SmallIntegerField(_("Изменение баллов доверия"))  # напр. -20
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Лог доверия")
        verbose_name_plural = _("Логи доверия")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at} — {self.reason} ({self.delta})"
