from django.shortcuts import redirect
from django.contrib.auth import login
from django.conf import settings
from .oidc import oauth
from apps.participants.models import PersonProfile
from .logger import logger

def login_view(request):
    try:
        # Используем настройки Django для формирования URL
        protocol = 'https' if not settings.DEBUG else 'http'
        host = request.get_host()  # Это вернет host:port
        redirect_uri = f"{protocol}://{host}/accounts/callback/"
        
        logger.info(f"Starting OIDC login process. Redirect URI: {redirect_uri}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        logger.debug(f"OAuth client config: {oauth.keycloak.client_kwargs}")
        
        return oauth.keycloak.authorize_redirect(request, redirect_uri)
    except Exception as e:
        logger.error(f"Error in login_view: {str(e)}", exc_info=True)
        raise

def callback(request):
    try:
        logger.info("Received callback from Keycloak")
        logger.debug(f"Callback request parameters: {dict(request.GET)}")
        
        # Проверяем наличие кода авторизации
        if 'code' not in request.GET:
            logger.error("No authorization code in callback")
            return redirect(settings.LOGIN_URL)
            
        # Проверяем state для предотвращения CSRF
        if 'state' not in request.GET:
            logger.error("No state parameter in callback")
            return redirect(settings.LOGIN_URL)
            
        logger.debug(f"Token endpoint: {settings.OIDC_OP_TOKEN_ENDPOINT}")
        
        # Получаем токен
        token = oauth.keycloak.authorize_access_token(request)
        if not token:
            logger.error("Failed to get access token")
            return redirect(settings.LOGIN_URL)
            
        logger.debug(f"Received token: {token}")
        
        # Получаем информацию о пользователе из токена
        userinfo = token.get('userinfo', {})
        if not userinfo:
            logger.error("No userinfo in token")
            return redirect(settings.LOGIN_URL)
            
        logger.info(f"Received userinfo: {userinfo}")
        
        # Проверяем наличие email
        if 'email' not in userinfo:
            logger.error("No email in userinfo")
            return redirect(settings.LOGIN_URL)
        
        # Получаем или создаем профиль пользователя
        try:
            # Получаем данные из userinfo
            email = userinfo.get('email', '')
            full_name = userinfo.get('name', '')
            iin = userinfo.get('preferred_username', '')[:12]  # Используем preferred_username как IIN
            
            logger.debug(f"User data from Keycloak - Email: {email}, Name: {full_name}, IIN: {iin}")
            
            # Создаем или обновляем профиль
            profile, created = PersonProfile.objects.update_or_create(
                email=email,
                defaults={
                    'full_name': full_name,
                    'iin': iin,
                }
            )
            
            logger.info(f"{'Created' if created else 'Updated'} profile for user: {profile.email}")
            
            # Создаем сессию для пользователя
            request.session['user_id'] = profile.id
            request.session['user_email'] = profile.email
            
            # Добавляем профиль в request для использования в шаблонах
            request.user_profile = profile
            
            # Сохраняем сессию
            request.session.save()
            
            logger.info(f"User {profile.email} successfully authenticated")
            return redirect(settings.LOGIN_REDIRECT_URL)
        except Exception as e:
            logger.error(f"Error creating/retrieving profile: {str(e)}", exc_info=True)
            return redirect(settings.LOGIN_URL)
            
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}", exc_info=True)
        logger.error(f"Request data: {request.GET}")
        return redirect(settings.LOGIN_URL)

def logout(request):
    try:
        user_email = request.session.get('user_email')
        logger.info(f"Logging out user: {user_email}")
        
        request.session.flush()
        logger.info(f"User {user_email} successfully logged out")
        
        return redirect(settings.LOGOUT_REDIRECT_URL)
    except Exception as e:
        logger.error(f"Error in logout: {str(e)}", exc_info=True)
        raise
