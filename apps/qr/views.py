from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest
from django.utils.timezone import now, localtime

from apps.groups.models import Session
from apps.participants.models import PersonProfile, BrowserFingerprint
from apps.attendance.models import Attendance, TrustLog


def penalize_fingerprint(fingerprint, reason, delta, attendance=None):
    old_score = fingerprint.trust_score
    new_score = max(0, old_score + delta)
    if new_score != old_score:
        fingerprint.trust_score = new_score
        fingerprint.save(update_fields=["trust_score"])
        TrustLog.objects.create(
            fingerprint=fingerprint,
            attendance=attendance,
            reason=reason,
            delta=delta,
        )


def mark_qr_page(request, token):
    iin = request.GET.get("iin")
    fingerprint_hash = request.GET.get("fp")

    if not iin or not fingerprint_hash:
        return render(request, "qr/mark.html", {"token": token})

    profile = get_object_or_404(PersonProfile, iin=iin)
    session = get_object_or_404(Session, qr_token_entry=token)

    current_dt = localtime()
    current_time = current_dt.time()

    if not (session.entry_start <= current_time <= session.entry_end):
        return render(request, "qr/mark_invalid.html", {
            "reason": "Время отметки не входит в допустимый интервал.",
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

    # 🚨 Проверка: один fingerprint использован для другого участника
    others = BrowserFingerprint.objects.filter(
        fingerprint_hash=fingerprint_hash
    ).exclude(profile=profile)
    if others.exists():
        penalize_fingerprint(
            fingerprint,
            reason="Один и тот же отпечаток использован разными участниками",
            delta=-30,
        )

    # 🚨 Проверка: fingerprint уже был в этой группе
    existing = Attendance.objects.filter(
        session=session,
        fingerprint_hash=fingerprint_hash
    ).exclude(profile=profile)
    if existing.exists():
        penalize_fingerprint(
            fingerprint,
            reason="Повторное использование отпечатка в одной сессии",
            delta=-20,
        )

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

    if not (session.exit_start <= current_time <= session.exit_end):
        return render(request, "qr/mark_invalid.html", {
            "reason": "Время отметки выхода не входит в допустимый интервал.",
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
