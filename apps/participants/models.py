from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class ParticipantProfile(models.Model):
    iin = models.CharField(_("ИИН"), max_length=12, unique=True)
    full_name = models.CharField(_("ФИО"), max_length=255)
    email = models.EmailField(_("Email"), blank=True)

    def __str__(self):
        return f"{self.full_name} ({self.iin})"

    class Meta:
        verbose_name = _("Профиль участника")
        verbose_name_plural = _("Профили участников")
        ordering = ["full_name"]


class BrowserFingerprint(models.Model):
    class TrustLevel(models.TextChoices):
        TRUSTED = "trusted", _("Доверенный")
        SUSPICIOUS = "suspicious", _("Подозрительный")
        BLOCKED = "blocked", _("Заблокирован")

    profile = models.ForeignKey(
        ParticipantProfile,
        on_delete=models.CASCADE,
        related_name="fingerprints",
        verbose_name=_("Профиль")
    )

    fingerprint_hash = models.CharField(_("Хэш отпечатка"), max_length=64)
    user_agent = models.TextField(_("User-Agent"))

    first_seen = models.DateTimeField(_("Первое появление"), auto_now_add=True)
    last_seen = models.DateTimeField(_("Последнее появление"), default=timezone.now)

    trust_score = models.PositiveSmallIntegerField(_("Оценка доверия (0–100)"), default=100)

    class Meta:
        unique_together = ("profile", "fingerprint_hash")
        indexes = [
            models.Index(fields=["fingerprint_hash"]),
            models.Index(fields=["profile", "last_seen"]),
        ]
        verbose_name = _("Отпечаток браузера")
        verbose_name_plural = _("Отпечатки браузеров")

    def __str__(self):
        return f"{self.profile.full_name} — {self.trust_level_display} ({self.trust_score}%)"

    @property
    def trust_level(self) -> str:
        """Определение уровня доверия на основе баллов"""
        if self.trust_score >= 80:
            return self.TrustLevel.TRUSTED
        elif self.trust_score >= 50:
            return self.TrustLevel.SUSPICIOUS
        return self.TrustLevel.BLOCKED
