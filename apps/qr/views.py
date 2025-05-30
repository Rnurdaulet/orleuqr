from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest
from django.utils.timezone import now, localtime

from apps.groups.models import Session
from apps.participants.models import PersonProfile, BrowserFingerprint
from apps.attendance.models import Attendance, TrustLog
from apps.attendance.utils import penalize_fingerprint, check_fingerprint_usage_conflicts


def mark_qr_page(request, token):
    iin = request.GET.get("iin")
    fingerprint_hash = request.GET.get("fp")

    if not iin or not fingerprint_hash:
        return render(request, "qr/mark.html", {"token": token})

    profile = get_object_or_404(PersonProfile, iin=iin)
    session = get_object_or_404(Session, qr_token_entry=token)

    current_dt = localtime()
    current_time = current_dt.time()

    if session.date != current_dt.date():
        return render(request, "qr/mark_invalid.html", {
            "reason": "Отметка возможна только в день проведения сессии.",
        })

    if session.date != current_dt.date():
        return render(request, "qr/mark_invalid.html", {
            "reason": "Сегодня не день сессии.",
        })

    if current_time < session.entry_start:
        return render(request, "qr/mark_invalid.html", {
            "reason": "Слишком рано для отметки входа.",
        })

    if current_time > session.entry_end:
        return render(request, "qr/mark_invalid.html", {
            "reason": "Слишком поздно для отметки входа.",
        })

    fingerprint, created = BrowserFingerprint.objects.get_or_create(
        profile=profile,
        fingerprint_hash=fingerprint_hash,
        defaults={
            "user_agent": request.headers.get("User-Agent", "")[:1000],
            "last_seen": current_dt,
        }
    )
    if not created:
        fingerprint.last_seen = current_dt
        fingerprint.save(update_fields=["last_seen"])

    check_fingerprint_usage_conflicts(fingerprint, profile, session)

    attendance, created = Attendance.objects.get_or_create(
        session=session,
        profile=profile,
        defaults={
            "arrived_at": current_dt,
            "trust_level": fingerprint.trust_level,
            "trust_score": fingerprint.trust_score,
            "fingerprint_hash": fingerprint_hash,
        }
    )

    if not created:
        return render(request, "qr/mark_already.html", {
            "attendance": attendance,
            "fingerprint": fingerprint,
        })

    return render(request, "qr/mark_success.html", {
        "attendance": attendance,
        "fingerprint": fingerprint,
    })


def mark_qr_exit_page(request, token):
    iin = request.GET.get("iin")
    fingerprint_hash = request.GET.get("fp")

    if not iin or not fingerprint_hash:
        return render(request, "qr/mark.html", {"token": token, "mode": "exit"})

    profile = get_object_or_404(PersonProfile, iin=iin)
    session = get_object_or_404(Session, qr_token_exit=token)

    current_dt = localtime()
    current_time = current_dt.time()

    if session.date != current_dt.date():
        return render(request, "qr/mark_invalid.html", {
            "reason": "Отметка возможна только в день проведения сессии.",
        })

    if current_time < session.exit_start:
        return render(request, "qr/mark_invalid.html", {
            "reason": "Слишком рано для отметки выхода.",
        })

    if current_time > session.exit_end:
        return render(request, "qr/mark_invalid.html", {
            "reason": "Слишком поздно для отметки выхода.",
        })

    fingerprint, created = BrowserFingerprint.objects.get_or_create(
        profile=profile,
        fingerprint_hash=fingerprint_hash,
        defaults={
            "user_agent": request.headers.get("User-Agent", "")[:1000],
            "last_seen": current_dt,
        }
    )
    if not created:
        fingerprint.last_seen = current_dt
        fingerprint.save(update_fields=["last_seen"])
    check_fingerprint_usage_conflicts(fingerprint, profile, session)
    attendance = Attendance.objects.filter(session=session, profile=profile).first()
    if not attendance:
        return render(request, "qr/mark_invalid.html", {
            "reason": "Отметка входа не найдена — нельзя выйти.",
        })

    if attendance.left_at:
        return render(request, "qr/mark_already.html", {
            "attendance": attendance,
            "fingerprint": fingerprint,
        })

    attendance.left_at = current_dt
    attendance.save(update_fields=["left_at"])

    return render(request, "qr/mark_success.html", {
        "attendance": attendance,
        "fingerprint": fingerprint,
        "is_exit": True,
    })
