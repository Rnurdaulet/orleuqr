import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.participants.models import PersonProfile
from apps.accounts.models import User


class Group(models.Model):
    external_id = models.IntegerField(unique=True, verbose_name=_("ID из внешней системы"))
    code = models.CharField(_("Код группы"), max_length=10, unique=True)
    course_name = models.TextField(_("Название курса"))
    supervisor_name = models.CharField(_("ФИО тренера"), max_length=255)
    supervisor_iin = models.CharField(_("ИИН тренера"), max_length=12)
    start_date = models.DateField(_("Дата начала"))
    end_date = models.DateField(_("Дата окончания"))

    participants = models.ManyToManyField(
        PersonProfile,
        related_name="groups",
        verbose_name=_("Участники")
    )
    trainers = models.ManyToManyField(
        PersonProfile,
        related_name="trainer_groups",
        verbose_name=_("Тренеры")
    )

    def __str__(self):
        return f"{self.code} — {self.course_name}"

    class Meta:
        verbose_name = _("Группа")
        verbose_name_plural = _("Группы")
        ordering = ["-start_date"]


import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Session(models.Model):
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name=_("Группа"),
    )
    date = models.DateField(_("Дата"))

    # Временные окна
    entry_start = models.TimeField(_("Вход: начало"), default="09:00")
    entry_end = models.TimeField(_("Вход: конец"), default="10:00")
    exit_start = models.TimeField(_("Выход: начало"), default="17:00")
    exit_end = models.TimeField(_("Выход: конец"), default="18:00")

    # Разные QR-токены на вход и выход
    qr_token_entry = models.UUIDField(_("QR токен (вход)"), unique=True, default=uuid.uuid4)
    qr_token_exit = models.UUIDField(_("QR токен (выход)"), unique=True, default=uuid.uuid4)

    class Meta:
        unique_together = ("group", "date")
        ordering = ["group", "date"]
        verbose_name = _("Сессия")
        verbose_name_plural = _("Сессии")

    def __str__(self):
        return f"{self.group.code} — {self.date}"
