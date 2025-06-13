import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils.timezone import now, localdate
from django.shortcuts import get_object_or_404

from apps.accounts.decorators import sso_login_required
from apps.qr.services import manual_mark_entry
from apps.participants.models import PersonProfile
from apps.groups.models import Session

logger = logging.getLogger("attendance")


@csrf_exempt
@require_POST
@sso_login_required
def manual_mark_view(request):
    try:
        data = json.loads(request.body)
        mark_type = data.get("type")
        session_id = data.get("session_id")
        participant_id = data.get("participant_id")

        if not session_id or not participant_id or mark_type not in ("entry", "exit"):
            return JsonResponse({"error": "Недостаточно данных"}, status=400)

        session = get_object_or_404(Session, id=session_id)
        if session.date != localdate():
            return JsonResponse({"error": "Можно отмечать только текущую дату"}, status=403)

        participant = get_object_or_404(PersonProfile, id=participant_id)
        trainer = request.user_profile

        success, result = manual_mark_entry(
            trainer_profile=trainer,
            participant_profile=participant,
            session=session,
            mark_type=mark_type
        )

        if success:
            logger.info(f"[ManualMark] {trainer.full_name} отметил {mark_type} участника {participant.full_name}")
            return JsonResponse({"ok": True})
        else:
            return JsonResponse({"error": str(result)}, status=400)

    except Exception as e:
        logger.exception("[ManualMark] Ошибка при отметке")
        return JsonResponse({"error": str(e)}, status=500)
