from django import forms
from apps.participants.models import PersonProfile
from apps.groups.models import Session
from apps.attendance.models import Attendance


class ManualMarkForm(forms.Form):
    profile = forms.ModelChoiceField(queryset=PersonProfile.objects.none(), label="Участник")
    session = forms.ModelChoiceField(queryset=Session.objects.none(), label="Сессия")
    mark_type = forms.ChoiceField(
        choices=[("entry", "Отметка входа"), ("exit", "Отметка выхода")],
        label="Тип отметки"
    )

    def __init__(self, *args, trainer=None, **kwargs):
        super().__init__(*args, **kwargs)

        if trainer:
            today_sessions = Session.objects.filter(group__trainers=trainer).values_list("date", flat=True).distinct()
            self.fields["session"].queryset = Session.objects.filter(group__trainers=trainer, date__in=today_sessions)

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

        try:
            attendance = Attendance.objects.get(session=session, profile=profile)
            if mark_type == "entry" and attendance.arrived_at:
                raise forms.ValidationError("Участник уже отмечен на вход.")
            if mark_type == "exit" and attendance.left_at:
                raise forms.ValidationError("Участник уже отмечен на выход.")
        except Attendance.DoesNotExist:
            if mark_type == "exit":
                raise forms.ValidationError("Нельзя отметить выход без входа.")

        return cleaned_data
