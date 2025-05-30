from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import localtime
from django.views.decorators.http import require_http_methods

from apps.participants.models import PersonProfile
from apps.attendance.models import Attendance, TrustLog
from apps.groups.models import Session

from .forms import ManualMarkForm


@require_http_methods(["GET", "POST"])
def manual_mark_view(request):
    iin = request.GET.get("iin")
    trainer = PersonProfile.objects.filter(iin=iin, role=PersonProfile.Role.TRAINER).first()
    if not trainer:
        messages.error(request, "Вы не зарегистрированы как тренер.")
        return redirect("/")

    today = localtime().date()
    sessions = Session.objects.filter(group__trainers=trainer, date=today).select_related("group")

    if request.method == "POST":
        form = ManualMarkForm(request.POST, trainer=trainer)
        if form.is_valid():
            profile = form.cleaned_data["profile"]
            session = form.cleaned_data["session"]
            mark_type = form.cleaned_data["mark_type"]

            attendance, _ = Attendance.objects.get_or_create(
                session=session,
                profile=profile,
                defaults={
                    "trust_level": "manual_by_trainer",
                    "trust_score": 0,
                    "fingerprint_hash": f"manual-mark-{trainer.iin}",
                }
            )

            if mark_type == "entry" and not attendance.arrived_at:
                attendance.arrived_at = localtime()
                attendance.save(update_fields=["arrived_at"])
            elif mark_type == "exit":
                if not attendance.arrived_at:
                    messages.error(request, "Сначала необходимо отметить вход.")
                    return redirect(request.path)
                if not attendance.left_at:
                    attendance.left_at = localtime()
                    attendance.save(update_fields=["left_at"])

            TrustLog.objects.create(
                fingerprint=None,
                attendance=attendance,
                reason=f"Ручная отметка ({mark_type}) тренером {trainer.full_name} ({trainer.iin})",
                delta=-10
            )

            messages.success(request, f"{profile.full_name} успешно отмечен на {mark_type}.")
            return redirect(request.path)
        else:
            messages.error(request, "Форма заполнена некорректно.")
    else:
        form = ManualMarkForm(trainer=trainer)

    return render(request, "attendance/manual_mark.html", {
        "trainer": trainer,
        "sessions": sessions,
        "form": form,
    })
