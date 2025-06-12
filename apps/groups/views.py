from collections import defaultdict
from django.db.models import Prefetch, Q
from django.shortcuts import render
from django.utils.timezone import now

from apps.accounts.decorators import sso_login_required
from apps.attendance.models import Attendance
from apps.groups.models import Group


@sso_login_required
def my_groups_view(request):
    today = now().date()
    user = request.user_profile

    groups = (
        Group.objects
        .filter(
            Q(participants=user) | Q(trainers=user),
            end_date__gte=today
        )
        .distinct()
        .prefetch_related("sessions", "participants", "trainers")
        .order_by("start_date")
    )

    attendance_map = defaultdict(lambda: defaultdict(dict))  # group_id -> session_id -> profile_id -> attendance

    trainer_groups = groups.filter(trainers=user)
    sessions_ids = []
    for group in trainer_groups:
        sessions_ids.extend([s.id for s in group.sessions.all()])

    attendances = Attendance.objects.filter(
        session_id__in=sessions_ids
    ).select_related("profile", "marked_by_trainer", "session")

    for att in attendances:
        attendance_map[att.session.group_id][att.session_id][att.profile_id] = att

    return render(request, "groups/my_groups.html", {
        "groups": groups,
        "user": user,
        "attendance_map": attendance_map,
    })


from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from apps.groups.models import Session
from apps.groups.services import generate_session_qr_pdf_on_fly


def session_qr_pdf_view(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    if request.method == "POST":
        mode = request.POST.get("mode", "entry")
        pdf_bytes = generate_session_qr_pdf_on_fly(session.id, mode=mode)
        if pdf_bytes:
            filename = f"QR_{session.group.code}_{session.date}_{mode}.pdf"
            resp = HttpResponse(pdf_bytes, content_type="application/pdf")
            resp["Content-Disposition"] = f'attachment; filename="{filename}"'
            return resp
        else:
            messages.error(request, "Ошибка при генерации PDF.")
    return render(request, "groups/session_qr_pdf.html", {"session": session})