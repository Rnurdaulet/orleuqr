from django import forms
from apps.participants.models import PersonProfile
from apps.groups.models import Session
from apps.attendance.models import Attendance
from django.utils import timezone

class ManualMarkForm(forms.Form):
    profile = forms.ModelChoiceField(queryset=PersonProfile.objects.none(), label="Участник")
    session = forms.ModelChoiceField(queryset=Session.objects.none(), label="Сессия")
    mark_type = forms.ChoiceField(
        choices=[("entry", "Отметка входа"), ("exit", "Отметка выхода")],
        label="Тип отметки"
    )

    def __init__(self, *args, trainer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.trainer = trainer

        if trainer:
            today = timezone.localdate()
            self.fields["session"].queryset = Session.objects.filter(group__trainers=trainer, date=today)
            self.fields["profile"].queryset = PersonProfile.objects.filter(
                groups__in=trainer.trainer_groups.all(),
                role=PersonProfile.Role.PARTICIPANT
            ).distinct()

    def clean(self):
        cleaned_data = super().clean()
        session = cleaned_data.get("session")
        profile = cleaned_data.get("profile")
        mark_type = cleaned_data.get("mark_type")

        if not session or not profile:
            return cleaned_data

        if self.trainer and session.group not in self.trainer.trainer_groups.all():
            raise forms.ValidationError("Вы не можете отмечать участников в этой сессии.")

        if session.date != timezone.localdate():
            raise forms.ValidationError("Можно отмечать только сегодняшние сессии.")

        try:
            attendance = Attendance.objects.get(session=session, profile=profile)
            if mark_type == "entry" and attendance.arrived_at:
                self.add_error("mark_type", "Участник уже отмечен на вход.")
            elif mark_type == "exit":
                if not attendance.arrived_at:
                    self.add_error("mark_type", "Нельзя отметить выход без входа.")
                elif attendance.left_at:
                    self.add_error("mark_type", "Участник уже отмечен на выход.")
        except Attendance.DoesNotExist:
            if mark_type == "exit":
                self.add_error("mark_type", "Нельзя отметить выход без входа.")

        return cleaned_data
