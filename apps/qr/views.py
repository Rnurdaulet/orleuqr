from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest
from django.utils.timezone import now, localtime

from apps.groups.models import Session
from apps.participants.models import ParticipantProfile, BrowserFingerprint
from apps.attendance.models import Attendance


def mark_qr_page(request, token):
    iin = request.GET.get("iin")
    fingerprint_hash = request.GET.get("fp")

    # Если нет IIN или fingerprint, отдаем страницу для JS и сбора данных
    if not iin or not fingerprint_hash:
        return render(request, "qr/mark.html", {"token": token})

    # Получаем профиль и сессию
    profile = get_object_or_404(ParticipantProfile, iin=iin)
    session = get_object_or_404(Session, qr_token_entry=token)

    # Локальное время и его проверка на допустимый интервал входа
    current_dt = localtime()
    current_time = current_dt.time()

    if not (session.entry_start <= current_time <= session.entry_end):
        return render(request, "qr/mark_invalid.html", {
            "reason": "Время отметки не входит в допустимый интервал.",
        })

    # Обработка отпечатка браузера
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

    # Отметка посещения, если еще не было
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

    profile = get_object_or_404(ParticipantProfile, iin=iin)
    session = get_object_or_404(Session, qr_token_exit=token)

    current_dt = localtime()
    current_time = current_dt.time()

    print(current_time)
    print(session.exit_start)
    print(session.exit_end)

    if not (session.exit_start <= current_time <= session.exit_end):
        return render(request, "qr/mark_invalid.html", {
            "reason": "Время отметки выхода не входит в допустимый интервал.",
        })

    # обновляем или создаем fingerprint
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

    # ищем существующую отметку входа
    attendance = Attendance.objects.filter(session=session, profile=profile).first()
    if not attendance:
        return render(request, "qr/mark_invalid.html", {
            "reason": "Отметка входа не найдена — нельзя выйти.",
        })

    if attendance.left_at:
        return render(request, "qr/mark_already.html", {"attendance": attendance})

    attendance.left_at = current_dt
    attendance.save(update_fields=["left_at"])

    return render(request, "qr/mark_success.html", {
        "attendance": attendance,
        "fingerprint": fingerprint,
        "is_exit": True,
    })
