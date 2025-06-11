from django.shortcuts import redirect
from django.conf import settings
from apps.participants.models import PersonProfile
from .logger import logger

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Пропускаем проверку для URL-ов аутентификации
            if request.path.startswith('/accounts/'):
                logger.debug(f"Skipping authentication for path: {request.path}")
                return self.get_response(request)

            # Проверяем наличие пользователя в сессии
            user_id = request.session.get('user_id')
            logger.debug(f"Session data: {dict(request.session)}")
            
            if not user_id:
                logger.warning(f"No user_id in session for path: {request.path}")
                return redirect(settings.LOGIN_URL)

            try:
                # Проверяем существование профиля
                profile = PersonProfile.objects.get(id=user_id)
                logger.debug(f"Found profile: id={profile.id}, email={profile.email}, full_name={profile.full_name}, iin={profile.iin}")
                
                # Добавляем профиль в request
                request.user_profile = profile
                logger.debug(f"Added profile to request: {request.user_profile}")
                
                # Проверяем, что профиль действительно добавлен
                if hasattr(request, 'user_profile'):
                    logger.debug(f"Profile in request: id={request.user_profile.id}, email={request.user_profile.email}")
                else:
                    logger.error("Profile was not added to request!")
                
                logger.debug(f"Authenticated user {profile.email} accessing {request.path}")
            except PersonProfile.DoesNotExist:
                logger.error(f"Profile not found for user_id: {user_id}")
                request.session.flush()
                return redirect(settings.LOGIN_URL)

            response = self.get_response(request)
            
            # Проверяем, что профиль все еще доступен после обработки запроса
            if hasattr(request, 'user_profile'):
                logger.debug(f"Profile still in request after response: {request.user_profile.email}")
            else:
                logger.error("Profile was lost after response!")
                
            return response
            
        except Exception as e:
            logger.error(f"Error in AuthenticationMiddleware: {str(e)}", exc_info=True)
            raise 