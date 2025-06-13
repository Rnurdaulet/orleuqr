from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from apps.attendance.models import Attendance

@csrf_exempt
@require_POST
@login_required
def manual_mark_view(request):
    try:
        data = json.loads(request.body)
        attendance_id = data.get("id")
        mark_type = data.get("type")

        trainer = getattr(request, "user_profile", None) or request.user

        if attendance_id:
            att = get_object_or_404(Attendance, id=attendance_id)
        else:
            # Новая отметка: создаём attendance
            session_id = data.get("session_id")
            profile_id = data.get("participant_id")
            if not session_id or not profile_id:
                return JsonResponse({"error": "Не хватает данных"}, status=400)

            att, _ = Attendance.objects.get_or_create(
                session_id=session_id,
                profile_id=profile_id,
                defaults={"trust_score": 100, "trust_level": "manual_by_trainer"}
            )

        # Проставляем ручную отметку
        if mark_type == "entry":
            att.marked_entry_by_trainer = trainer
            if not att.arrived_at:
                att.arrived_at = now()
        elif mark_type == "exit":
            att.marked_exit_by_trainer = trainer
            if not att.left_at:
                att.left_at = now()
        else:
            return JsonResponse({"error": "Недопустимый тип"}, status=400)

        att.save()
        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
