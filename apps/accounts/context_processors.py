from .logger import logger
from apps.participants.models import PersonProfile

def user_profile(request):
    """
    Добавляет профиль пользователя в контекст шаблона
    """
    try:
        user_id = request.session.get('user_id')
        if user_id:
            try:
                profile = PersonProfile.objects.get(id=user_id)
                logger.debug(f"Adding user_profile to template context: {profile}")
                return {'user_profile': profile}
            except PersonProfile.DoesNotExist:
                logger.error(f"Profile not found for user_id: {user_id}")
                return {'user_profile': None}
        else:
            logger.debug("No user_id in session")
            return {'user_profile': None}
    except Exception as e:
        logger.error(f"Error in user_profile context processor: {str(e)}", exc_info=True)
        return {'user_profile': None} 