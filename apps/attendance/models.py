from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.groups.models import Session
from apps.participants.models import PersonProfile
from apps.core.models import BaseModel


class Attendance(BaseModel):
    class TrustLevel(models.TextChoices):
        TRUSTED = "trusted", _("Доверенный")
        SUSPICIOUS = "suspicious", _("Подозрительный")
        BLOCKED = "blocked", _("Заблокирован")
        MANUAL = "manual_by_trainer", _("Ручная отметка")

    class TimeStatus(models.TextChoices):
        MANUAL = "by_trainer", _("Ручная отметка")
        TOO_EARLY = "too_early", _("Рано")
        ON_TIME = "on_time", _("Во время")
        TOO_LATE = "too_late", _("Опоздал")
        UNKNOWN = "unknown", _("Неизвестно")

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
    arrived_status = models.CharField(
        _("Статус входа"),
        max_length=20,
        choices=TimeStatus.choices,
        default=TimeStatus.UNKNOWN,
    )
    left_status = models.CharField(
        _("Статус выхода"),
        max_length=20,
        choices=TimeStatus.choices,
        default=TimeStatus.UNKNOWN,
    )
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
    marked_entry_by_trainer = models.ForeignKey(
        PersonProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Вход отмечен вручную"),
        related_name="manual_entry_attendances",
    )

    marked_exit_by_trainer = models.ForeignKey(
        PersonProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Выход отмечен вручную"),
        related_name="manual_exit_attendances",
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

    def is_suspicious(self):
        return self.trust_level in {
            self.TrustLevel.SUSPICIOUS,
            self.TrustLevel.BLOCKED,
        } or self.trust_score < 50

    def status_label(self):
        if self.left_at and self.arrived_at:
            return _("Посетил полностью")
        elif self.arrived_at:
            return _("Только вход")
        elif self.left_at:
            return _("Только выход")
        return _("Отсутствует")

    @classmethod
    def for_group(cls, group):
        return cls.objects.filter(session__group=group).select_related("profile", "session")


class TrustLog(models.Model):
    fingerprint = models.ForeignKey("participants.BrowserFingerprint", on_delete=models.CASCADE, null=True, blank=True)
    attendance = models.ForeignKey("attendance.Attendance", on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=255)
    delta = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.fingerprint and not self.attendance:
            raise ValueError("TrustLog must be linked to either fingerprint or attendance.")
        super().save(*args, **kwargs)
