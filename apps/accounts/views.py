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

        logger.info(f"Starting OIDC login process. Redirect URI: {redirect_uri}")
        return oauth.keycloak.authorize_redirect(request, redirect_uri)

    except Exception as e:
        logger.error(f"Error in login_view: {str(e)}", exc_info=True)
        raise


def callback(request):
    try:
        logger.info("Received callback from Keycloak")
        logger.debug(f"Callback GET params: {dict(request.GET)}")

        if 'code' not in request.GET or 'state' not in request.GET:
            logger.error("Missing 'code' or 'state' in callback request")
            return redirect(settings.LOGIN_URL)

        token = oauth.keycloak.authorize_access_token(request)
        access_token = token.get('access_token')
        userinfo = token.get('userinfo')

        if not access_token or not userinfo:
            logger.error("Access token or userinfo missing in OIDC response")
            return redirect(settings.LOGIN_URL)

        logger.info(f"Userinfo received: {userinfo}")

        # Валидация email и IIN
        email = userinfo.get('email')
        if not email or '@' not in email:
            logger.error(f"Invalid or missing email: {email}")
            return redirect(settings.LOGIN_URL)

        raw_iin = userinfo.get('preferred_username', '')
        iin = raw_iin[:12] if len(raw_iin) >= 12 else None
        if not iin:
            logger.error(f"Invalid IIN from preferred_username: {raw_iin}")
            return redirect(settings.LOGIN_URL)

        full_name = userinfo.get('name', '')

        profile, created = PersonProfile.objects.update_or_create(
            email=email,
            defaults={
                'full_name': full_name,
                'iin': iin,
            }
        )

        logger.info(f"{'Created' if created else 'Updated'} profile: {profile.email}")

        request.session['user_id'] = profile.id
        request.session['user_email'] = profile.email
        request.user_profile = profile
        request.session.save()

        logger.info(f"User {profile.email} authenticated")
        return redirect(settings.LOGIN_REDIRECT_URL)

    except Exception as e:
        logger.error(f"Error in callback: {str(e)}", exc_info=True)
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
