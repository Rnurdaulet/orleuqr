from authlib.integrations.django_client import OAuth
from django.conf import settings

oauth = OAuth()

oauth.register(
    name='keycloak',
    client_id=settings.OIDC_RP_CLIENT_ID,
    client_secret=settings.OIDC_RP_CLIENT_SECRET,
    authorize_url=settings.OIDC_OP_AUTHORIZATION_ENDPOINT,
    token_url=settings.OIDC_OP_TOKEN_ENDPOINT,
    userinfo_url=settings.OIDC_OP_USER_ENDPOINT,
    jwks_uri=settings.OIDC_OP_JWKS_ENDPOINT,
    client_kwargs={
        'scope': settings.OIDC_RP_SCOPES,
        'token_endpoint_auth_method': 'client_secret_post',
        'token_placement': 'header'
    },
    server_metadata_url=f"{settings.OIDC_OP_AUTHORIZATION_ENDPOINT.rsplit('/protocol/', 1)[0]}/.well-known/openid-configuration"
) 