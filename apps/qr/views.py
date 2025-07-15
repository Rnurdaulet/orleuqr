from django.shortcuts import render, redirect
from django.conf import settings
from django.utils.translation import gettext as _

from apps.accounts.decorators import sso_login_required
from apps.qr.services import mark_attendance

@sso_login_required
def mark_qr_page(request, token):
    profile = getattr(request, "user_profile", None)
    fingerprint_hash = request.GET.get("fp")

    if not profile:
        return redirect(settings.LOGIN_URL)

    if not fingerprint_hash:
        return render(request, "qr/mark.html", {"token": token})

    user_agent = request.headers.get("User-Agent", "")

    try:
        success, result, status = mark_attendance(
            profile=profile,
            token=token,
            fingerprint_hash=fingerprint_hash,
            user_agent=user_agent,
            mode='entry',
        )

        if success == "already_marked":
            return render(request, "qr/mark_already.html", {"attendance": result, "status": status})
        elif success:
            return render(request, "qr/mark_success.html", {"attendance": result, "status": status})
        else:
            return render(request, "qr/mark_invalid.html", {"reason": result, "status": status})
    except Exception as e:
        # Логируем ошибку для отладки
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in mark_qr_page: {str(e)}")
        
        return render(request, "qr/mark_invalid.html", {
            "reason": _("Произошла техническая ошибка. Пожалуйста, попробуйте еще раз или обратитесь к администратору."),
            "status": None
        })


@sso_login_required
def mark_qr_exit_page(request, token):
    profile = getattr(request, "user_profile", None)
    fingerprint_hash = request.GET.get("fp")

    if not profile:
        return redirect(settings.LOGIN_URL)

    if not fingerprint_hash:
        return render(request, "qr/mark.html", {"token": token, "mode": "exit"})

    user_agent = request.headers.get("User-Agent", "")

    try:
        success, result, status = mark_attendance(
            profile=profile,
            token=token,
            fingerprint_hash=fingerprint_hash,
            user_agent=user_agent,
            mode='exit',
        )

        if success == "already_marked":
            return render(request, "qr/mark_already.html", {"attendance": result, "status": status})
        elif success:
            return render(request, "qr/mark_success.html", {
                "attendance": result,
                "is_exit": True,
                "status": status,
            })
        else:
            return render(request, "qr/mark_invalid.html", {"reason": result, "status": status})
    except Exception as e:
        # Логируем ошибку для отладки
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in mark_qr_exit_page: {str(e)}")
        
        return render(request, "qr/mark_invalid.html", {
            "reason": _("Произошла техническая ошибка. Пожалуйста, попробуйте еще раз или обратитесь к администратору."),
            "status": None
        })

@sso_login_required
def qr_scan_page(request):
    return render(request, "qr/scan.html")