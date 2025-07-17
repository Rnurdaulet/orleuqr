from django.shortcuts import redirect
from django.conf import settings
from .oidc import oauth
from apps.participants.models import PersonProfile
from .logger import logger


def login_view(request):
    try:
        protocol = 'https' if not settings.DEBUG else 'http'
        host = request.get_host()
        # redirect_uri = f"{protocol}://{host}/accounts/callback/"
        redirect_uri = settings.SITE_BASE_URL.rstrip("/") + "/accounts/callback/"

        return oauth.keycloak.authorize_redirect(request, redirect_uri)

    except Exception as e:
        logger.error(f"Error in login_view: {str(e)}", exc_info=True)
        raise


def callback(request):
    try:
        if 'code' not in request.GET or 'state' not in request.GET:
            logger.warning("Missing 'code' or 'state' in callback request")
            return redirect(settings.LOGIN_URL)

        token = oauth.keycloak.authorize_access_token(request)
        access_token = token.get('access_token')
        id_token = token.get('id_token')
        userinfo = token.get('userinfo')

        if not access_token or not userinfo:
            logger.warning("Access token or userinfo missing in OIDC response")
            return redirect(settings.LOGIN_URL)

        # Валидация email и IIN
        email = userinfo.get('email')
        if not email or '@' not in email:
            logger.warning(f"Invalid or missing email")
            return redirect(settings.LOGIN_URL)

        raw_iin = userinfo.get('preferred_username', '')
        iin = raw_iin[:12] if len(raw_iin) >= 12 else None
        if not iin:
            logger.warning(f"Invalid IIN from preferred_username")
            return redirect(settings.LOGIN_URL)

        full_name = userinfo.get('name', '')

        profile, created = PersonProfile.objects.update_or_create(
            email=email,
            defaults={
                'full_name': full_name,
                'iin': iin,
            }
        )

        if created:
            logger.info(f"New user registered: {email}")

        request.session['user_id'] = profile.id
        request.session['user_email'] = profile.email
        # Сохраняем id_token для использования при logout
        if id_token:
            request.session['id_token'] = id_token
        request.user_profile = profile
        request.session.save()

        return redirect(settings.LOGIN_REDIRECT_URL)

    except Exception as e:
        logger.error(f"Error in callback: {str(e)}", exc_info=True)
        return redirect(settings.LOGIN_URL)


def logout(request):
    try:
        user_email = request.session.get('user_email')
        id_token = request.session.get('id_token')

        # Очищаем локальную сессию
        request.session.flush()

        # Определяем logout endpoint
        logout_endpoint = None
        
        # Сначала пробуем взять из настроек
        if hasattr(settings, 'OIDC_OP_LOGOUT_ENDPOINT') and settings.OIDC_OP_LOGOUT_ENDPOINT:
            logout_endpoint = settings.OIDC_OP_LOGOUT_ENDPOINT
        # Если не задан, пытаемся сформировать автоматически на основе authorization endpoint
        elif hasattr(settings, 'OIDC_OP_AUTHORIZATION_ENDPOINT') and settings.OIDC_OP_AUTHORIZATION_ENDPOINT:
            auth_endpoint = settings.OIDC_OP_AUTHORIZATION_ENDPOINT
            # Для Keycloak: заменяем /auth на /logout
            if '/protocol/openid-connect/auth' in auth_endpoint:
                logout_endpoint = auth_endpoint.replace('/auth', '/logout')

        # Если есть id_token и logout endpoint, перенаправляем на Keycloak logout
        if id_token and logout_endpoint:
            # Формируем URL для logout в Keycloak
            logout_url = f"{logout_endpoint}?id_token_hint={id_token}"
            
            # Добавляем post_logout_redirect_uri только если включено в настройках
            if getattr(settings, 'OIDC_USE_POST_LOGOUT_REDIRECT', True):
                post_logout_redirect_uri = settings.SITE_BASE_URL.rstrip("/") + settings.LOGOUT_REDIRECT_URL
                logout_url += f"&post_logout_redirect_uri={post_logout_redirect_uri}"
            
            return redirect(logout_url)

        return redirect(settings.LOGOUT_REDIRECT_URL)

    except Exception as e:
        logger.error(f"Error in logout: {str(e)}", exc_info=True)
        return redirect(settings.LOGOUT_REDIRECT_URL)
