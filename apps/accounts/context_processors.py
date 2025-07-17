from .logger import logger
from apps.participants.models import PersonProfile

def user_profile(request):
    """
    Добавляет профиль пользователя в контекст шаблона.
    Если request.user_profile уже есть (например, из middleware) — использует его.
    Иначе — пробует получить из сессии.
    """
    try:
        # Приоритет — уже установлено middleware
        profile = getattr(request, 'user_profile', None)
        if profile:
            return {'user_profile': profile}

        user_id = request.session.get('user_id')
        if not user_id:
            return {'user_profile': None}

        try:
            profile = PersonProfile.objects.get(id=int(user_id))
            return {'user_profile': profile}
        except (PersonProfile.DoesNotExist, ValueError, TypeError) as e:
            logger.warning(f"Invalid or missing profile for user_id={user_id}")
            return {'user_profile': None}

    except Exception as e:
        logger.error(f"Unexpected error in user_profile context processor: {str(e)}", exc_info=True)
        return {'user_profile': None}
