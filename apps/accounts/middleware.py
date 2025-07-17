from django.utils.deprecation import MiddlewareMixin
from apps.participants.models import PersonProfile
from .logger import logger

class AuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            user_id = request.session.get('user_id')
            if user_id:
                try:
                    profile = PersonProfile.objects.get(id=int(user_id))
                    request.user_profile = profile
                except (PersonProfile.DoesNotExist, ValueError, TypeError) as e:
                    logger.warning(f"Invalid session or missing profile for user_id={user_id}")
                    request.session.flush()
                    request.user_profile = None
            else:
                request.user_profile = None
        except Exception as e:
            logger.error(f"Error in AuthenticationMiddleware: {str(e)}", exc_info=True)
            raise
