from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class BasePersonProfile(models.Model):
    iin = models.CharField(_("ИИН"), max_length=12, unique=True, db_index=True)
    full_name = models.CharField(_("ФИО"), max_length=255, db_index=True)
    email = models.EmailField(_("Email"), blank=True)

    class Meta:
        abstract = True
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.iin})"


class ParticipantProfile(BasePersonProfile):
    class Meta(BasePersonProfile.Meta):
        verbose_name = _("Профиль участника")
        verbose_name_plural = _("Профили участников")


class TrainerProfile(BasePersonProfile):
    class Meta(BasePersonProfile.Meta):
        verbose_name = _("Профиль тренера")
        verbose_name_plural = _("Профили тренеров")


class BrowserFingerprint(models.Model):
    class TrustLevel(models.TextChoices):
        TRUSTED = "trusted", _("Доверенный")
        SUSPICIOUS = "suspicious", _("Подозрительный")
        BLOCKED = "blocked", _("Заблокирован")

    profile = models.ForeignKey(
        ParticipantProfile,
        on_delete=models.CASCADE,
        related_name="fingerprints",
        verbose_name=_("Профиль"),
        db_index=True
    )

    fingerprint_hash = models.CharField(_("Хэш отпечатка"), max_length=64)
    user_agent = models.TextField(_("User-Agent"))
    first_seen = models.DateTimeField(_("Первое появление"), auto_now_add=True)
    last_seen = models.DateTimeField(_("Последнее появление"), default=timezone.now)

    trust_score = models.PositiveSmallIntegerField(
        _("Оценка доверия (0–100)"),
        default=100,
        help_text=_("Вычисляется автоматически при отметке")
    )

    class Meta:
        unique_together = ("profile", "fingerprint_hash")
        indexes = [
            models.Index(fields=["fingerprint_hash"]),
            models.Index(fields=["profile", "last_seen"]),
            models.Index(fields=["trust_score"]),
        ]
        verbose_name = _("Отпечаток браузера")
        verbose_name_plural = _("Отпечатки браузеров")

    def __str__(self):
        return f"{self.profile.full_name} — {self.get_trust_level_display()} ({self.trust_score}%)"

    @property
    def trust_level(self) -> str:
        if self.trust_score >= 80:
            return self.TrustLevel.TRUSTED
        elif self.trust_score >= 50:
            return self.TrustLevel.SUSPICIOUS
        return self.TrustLevel.BLOCKED

    def get_trust_level_display(self):
        return dict(self.TrustLevel.choices).get(self.trust_level, "Неизвестно")
