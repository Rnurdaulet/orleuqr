from django.shortcuts import get_object_or_404
from django.utils.timezone import localtime
from django.utils.translation import gettext as _
from apps.groups.models import Session
from apps.participants.models import PersonProfile, BrowserFingerprint
from apps.attendance.models import Attendance, TrustLog
from apps.attendance.utils import check_fingerprint_usage_conflicts


def _get_session_by_token(token: str, mode: str):
    """Получить сессию по токену. Возвращает (session, error_message)"""
    try:
        if mode == 'entry':
            session = Session.objects.get(qr_token_entry=token)
        else:
            session = Session.objects.get(qr_token_exit=token)
        return session, None
    except Session.DoesNotExist:
        return None, _("QR-код недействителен или сессия не найдена. Возможно, код устарел или был удален.")


def _validate_session_time(session: Session, current_time, mode: str, use_time_limits: bool):
    current_date = localtime().date()
    if session.date != current_date:
        return False, _("Отметка возможна только в день проведения сессии."), None

    if not use_time_limits:
        # Разрешаем отметку в любое время, статус определим позже
        return True, None, None

    if mode == 'entry':
        if current_time < session.entry_start:
            return False, _("Слишком рано для отметки входа."), Attendance.TimeStatus.TOO_EARLY
        if current_time > session.entry_end:
            return False, _("Слишком поздно для отметки входа."), Attendance.TimeStatus.TOO_LATE
    else:
        if current_time < session.exit_start:
            return False, _("Слишком рано для отметки выхода."), Attendance.TimeStatus.TOO_EARLY
        if current_time > session.exit_end:
            return False, _("Слишком поздно для отметки выхода."), Attendance.TimeStatus.TOO_LATE

    return True, None, Attendance.TimeStatus.ON_TIME


def _calculate_time_status(event_time, start, end):
    if event_time < start:
        return Attendance.TimeStatus.TOO_EARLY
    elif event_time > end:
        return Attendance.TimeStatus.TOO_LATE
    else:
        return Attendance.TimeStatus.ON_TIME


def mark_attendance(profile: PersonProfile, token: str, fingerprint_hash: str, user_agent: str, mode: str = 'entry'):
    session, session_error = _get_session_by_token(token, mode)
    if session_error:
        return False, session_error, None
    
    current_time = localtime().time()
    use_time_limits = getattr(session.group, 'use_time_limits', False)

    valid, error, status = _validate_session_time(session, current_time, mode, use_time_limits)
    if not valid:
        return False, error, status

    if profile not in session.group.participants.all():
        return False, _("Вы не являетесь участником этой группы."), None

    fingerprint, created = BrowserFingerprint.objects.get_or_create(
        profile=profile,
        fingerprint_hash=fingerprint_hash,
        defaults={
            "user_agent": user_agent[:1000],
            "last_seen": localtime(),
        }
    )
    if not created:
        fingerprint.last_seen = localtime()
        fingerprint.save(update_fields=["last_seen"])

    check_fingerprint_usage_conflicts(fingerprint, profile, session)

    attendance = Attendance.objects.filter(session=session, profile=profile).first()
    now = localtime()

    if mode == 'entry':
        if attendance:
            return "already_marked", attendance, attendance.arrived_status

        arrived_status = status
        if not use_time_limits:
            arrived_status = _calculate_time_status(current_time, session.entry_start, session.entry_end)

        attendance = Attendance.objects.create(
            session=session,
            profile=profile,
            arrived_at=now,
            arrived_status=arrived_status,
            trust_level=fingerprint.trust_level,
            trust_score=fingerprint.trust_score,
            fingerprint_hash=fingerprint_hash,
        )
        return True, attendance, arrived_status

    elif mode == 'exit':
        if not attendance or not attendance.arrived_at:
            return False, _("Отметка входа не найдена — нельзя отметить выход."), attendance.left_status if attendance else None

        if attendance.left_at:
            return "already_marked", attendance, attendance.left_status

        left_status = status
        if not use_time_limits:
            left_status = _calculate_time_status(current_time, session.exit_start, session.exit_end)

        attendance.left_at = now
        attendance.left_status = left_status
        attendance.save(update_fields=["left_at", "left_status"])
        return True, attendance, left_status


def manual_mark_entry(trainer_profile: PersonProfile, participant_profile: PersonProfile, session: Session, mark_type: str):
    now = localtime()

    if session.group not in trainer_profile.trainer_groups.all():
        return False, _("Вы не связаны с этой группой.")

    if participant_profile not in session.group.participants.all():
        return False, _("Участник не входит в эту группу.")

    attendance, created = Attendance.objects.get_or_create(
        session=session,
        profile=participant_profile,
        defaults={
            "trust_level": Attendance.TrustLevel.MANUAL,
            "trust_score": 0,
            "fingerprint_hash": f"manual-mark-{trainer_profile.iin}",
            "arrived_status": Attendance.TimeStatus.UNKNOWN,
            "left_status": Attendance.TimeStatus.UNKNOWN,
        }
    )

    changed = False
    if mark_type == "entry" and not attendance.arrived_at:
        attendance.arrived_at = now
        attendance.arrived_status = Attendance.TimeStatus.MANUAL
        attendance.marked_entry_by_trainer = trainer_profile
        changed = True
    elif mark_type == "exit":
        if not attendance.arrived_at:
            return False, _("Сначала необходимо отметить вход.")
        if not attendance.left_at:
            attendance.left_at = now
            attendance.left_status = Attendance.TimeStatus.MANUAL
            attendance.marked_exit_by_trainer = trainer_profile
            changed = True

    if changed:
        attendance.save()
        fingerprint, created = BrowserFingerprint.objects.get_or_create(
            profile=trainer_profile,
            fingerprint_hash=f"manual-mark-{trainer_profile.iin}",
            defaults={
                "user_agent": "manual mark",
                "last_seen": now,
            }
        )
        if not created:
            fingerprint.last_seen = now
            fingerprint.save(update_fields=["last_seen"])

        TrustLog.objects.create(
            fingerprint=fingerprint,
            attendance=attendance,
            reason=_("Ручная отметка ({mark_type}) тренером {trainer} ({iin})").format(
                mark_type=mark_type,
                trainer=trainer_profile.full_name,
                iin=trainer_profile.iin,
            ),
            delta=-10,
        )
        return True, attendance
    else:
        return False, _("Отметка уже поставлена.")
