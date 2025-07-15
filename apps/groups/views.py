from collections import defaultdict
from django.db.models import Prefetch, Q
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now, localdate, localtime
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.contrib import messages

from apps.accounts.decorators import sso_login_required
from apps.attendance.models import Attendance
from apps.groups.models import Group, Session
from apps.groups.services import generate_session_qr_pdf_on_fly
from apps.participants.models import PersonProfile


# ------------------------------
# Участник: список своих групп
# ------------------------------
@sso_login_required
def participant_groups_view(request):
    today = now().date()
    user = request.user_profile

    groups = (
        Group.objects
        .filter(participants=user, end_date__gte=today)
        .prefetch_related("sessions", "trainers")
        .order_by("start_date")
    )

    attendance_map = defaultdict(lambda: defaultdict(dict))
    attendances = (
        Attendance.objects
        .filter(profile=user, session__group__in=groups)
        .select_related("session")
    )
    for att in attendances:
        attendance_map[att.session.group_id][att.session_id] = att

    return render(request, "groups/my_groups.html", {
        "groups": groups,
        "user": user,
        "attendance_map": attendance_map,
    })

# ------------------------------
# Тренер: список групп под управлением
# ------------------------------
@sso_login_required
def trainer_groups_view(request):
    today = now().date()
    user = request.user_profile

    groups = (
        Group.objects
        .filter(trainers=user, end_date__gte=today)
        .prefetch_related("sessions", "participants")
        .order_by("start_date")
    )

    return render(request, "groups/manage_groups.html", {
        "groups": groups,
        "user": user,
    })

# ------------------------------
# Тренер: подробная таблица посещаемости по группе
# ------------------------------
@sso_login_required
def group_detail_view(request, group_id):
    user = request.user_profile

    group = get_object_or_404(
        Group.objects.prefetch_related("sessions", "trainers"),
        id=group_id
    )

    if user.id not in {t.id for t in group.trainers.all()}:
        return HttpResponseForbidden("У вас нет доступа к этой группе")

    sessions = list(group.sessions.all().order_by("date"))

    return render(request, "groups/group_detail.html", {
        "group": group,
        "sessions": sessions,
    })

# ------------------------------
# JSON API: посещаемость участников группы
# ------------------------------

@sso_login_required
def attendance_json_view(request, group_id):
    user = request.user_profile

    group = get_object_or_404(
        Group.objects.prefetch_related("sessions", "participants", "trainers"),
        id=group_id
    )

    if user.id not in {t.id for t in group.trainers.all()}:
        return HttpResponseForbidden("У вас нет доступа к этой группе")

    sessions = list(group.sessions.all())
    participants = list(group.participants.all())

    session_lookup = {s.id: s.date.strftime("%Y-%m-%d") for s in sessions}
    attendance_lookup = {}

    for att in Attendance.for_group(group):
        attendance_lookup[(att.session_id, att.profile_id)] = att

    data = []

    for participant in participants:
        if not sessions:
            # Если нет сессий, просто возвращаем участника с "-"
            data.append({
                "participant_id": participant.id,
                "participant": participant.full_name,
                "date": "-",
                "session_id": None,
                "arrived_at": None,
                "left_at": None,
                "arrived_status": None,
                "left_status": None,
                "marked_entry": False,
                "marked_exit": False,
                "trust_level": None,
                "trust_score": None,
            })
            continue

        for session in sessions:
            att = attendance_lookup.get((session.id, participant.id))
            data.append({
                "participant_id": participant.id,
                "participant": participant.full_name,
                "date": session.date.strftime("%Y-%m-%d"),
                "session_id": session.id,
                "arrived_at": localtime(att.arrived_at).strftime("%H:%M") if att and att.arrived_at else None,
                "left_at": localtime(att.left_at).strftime("%H:%M") if att and att.left_at else None,
                "arrived_status": att.arrived_status if att else None,
                "left_status": att.left_status if att else None,
                "marked_entry": bool(att.marked_entry_by_trainer) if att else False,
                "marked_exit": bool(att.marked_exit_by_trainer) if att else False,
                "trust_level": att.get_trust_level_display() if att else None,
                "trust_score": att.trust_score if att else None,
            })

    return JsonResponse({"data": data})

# ------------------------------
# Ручная отметка: загрузка данных по участнику
# ------------------------------
@sso_login_required
def manual_attendance_data(request, group_id, participant_id):
    attendances = (
        Attendance.objects
        .filter(session__group_id=group_id, profile_id=participant_id)
        .select_related("session", "marked_entry_by_trainer", "marked_exit_by_trainer")
    )

    data = []
    for a in attendances:
        data.append({
            "id": a.id,
            "date": a.session.date.strftime("%Y-%m-%d"),
            "arrived_at": a.arrived_at.strftime("%H:%M") if a.arrived_at else None,
            "left_at": a.left_at.strftime("%H:%M") if a.left_at else None,
            "trust_level": a.get_trust_level_display(),
            "marked_entry": a.marked_entry_by_trainer.full_name if a.marked_entry_by_trainer else None,
            "marked_exit": a.marked_exit_by_trainer.full_name if a.marked_exit_by_trainer else None,
        })

    return JsonResponse({"attendances": data})


@sso_login_required
def participant_attendance_detail_view(request, group_id, participant_id):
    user = request.user_profile
    group = get_object_or_404(Group.objects.prefetch_related("sessions", "trainers"), id=group_id)
    participant = get_object_or_404(PersonProfile, id=participant_id)  # <-- исправлено

    if user not in group.trainers.all():
        return HttpResponseForbidden("Нет доступа к группе")

    sessions = group.sessions.all().order_by("date")
    attendance_by_session = {
        att.session_id: att for att in Attendance.objects.filter(
            session__group=group,
            profile=participant
        ).select_related("session", "marked_entry_by_trainer", "marked_exit_by_trainer")
    }

    return render(request, "groups/participant_detail.html", {
        "group": group,
        "participant": participant,
        "sessions": sessions,
        "attendance_by_session": attendance_by_session,
        "today": localdate(),
    })
# ------------------------------
# Генерация PDF с QR по сессии
# ------------------------------
@sso_login_required
def session_qr_pdf_view(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    if request.method == "POST":
        mode = request.POST.get("mode", "entry")
        pdf_bytes = generate_session_qr_pdf_on_fly(session.id, mode=mode)
        if pdf_bytes:
            filename = f"QR_{session.group.code}_{session.date}_{mode}.pdf"
            response = HttpResponse(pdf_bytes, content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        else:
            messages.error(request, "Ошибка при генерации PDF.")

    return render(request, "groups/session_qr_pdf.html", {"session": session})
