import logging
from functools import wraps
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext as _
from .models import APIToken

logger = logging.getLogger(__name__)

class APITokenMiddleware(MiddlewareMixin):
    """
    Middleware для проверки API токенов в заголовках Authorization
    """
    
    def process_request(self, request):
        """
        Проверяет наличие и валидность API токена
        """
        # Проверяем только запросы к API эндпоинтам
        if not self._is_api_request(request):
            return None
            
        # Извлекаем токен из заголовка
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token = self._extract_token(auth_header)
        
        if not token:
            return self._unauthorized_response("Отсутствует токен аутентификации")
        
        # Проверяем токен
        api_token = self._authenticate_token(token, request)
        if not api_token:
            return self._unauthorized_response("Недействительный токен")
        
        # Добавляем информацию о токене в request
        request.api_token = api_token
        request.api_authenticated = True
        
        # Обновляем время последнего использования
        api_token.update_last_used()
        
        logger.info(f"API request authenticated with token: {api_token.name}")
        return None
    
    def _is_api_request(self, request):
        """
        Определяет, является ли запрос API запросом
        """
        # Проверяем путь - для API эндпоинтов
        api_paths = ['/api/', '/webhook/']
        
        # Или проверяем заголовок Content-Type для JSON
        content_type = request.META.get('CONTENT_TYPE', '')
        
        return (
            any(request.path.startswith(path) for path in api_paths) or
            'application/json' in content_type or
            request.META.get('HTTP_AUTHORIZATION', '').startswith('Bearer ')
        )
    
    def _extract_token(self, auth_header):
        """
        Извлекает токен из заголовка Authorization
        Поддерживает форматы: 
        - Bearer <token>
        - Token <token>
        """
        if not auth_header:
            return None
            
        parts = auth_header.split()
        if len(parts) != 2:
            return None
            
        scheme, token = parts
        if scheme.lower() in ['bearer', 'token']:
            return token
            
        return None
    
    def _authenticate_token(self, token, request):
        """
        Аутентифицирует токен и проверяет права доступа
        """
        try:
            # Ищем токен по префиксу для оптимизации
            prefix = token[:8]
            api_tokens = APIToken.objects.filter(prefix=prefix, is_active=True)
            
            for api_token in api_tokens:
                if api_token.verify_token(token):
                    # Проверяем валидность токена
                    if not api_token.is_valid():
                        logger.warning(f"Invalid token used: {api_token.name}")
                        return None
                    
                    # Проверяем IP адрес
                    client_ip = self._get_client_ip(request)
                    if not api_token.check_ip_access(client_ip):
                        logger.warning(f"IP access denied for token {api_token.name} from {client_ip}")
                        return None
                    
                    return api_token
            
        except Exception as e:
            logger.error(f"Error authenticating token: {str(e)}")
        
        return None
    
    def _get_client_ip(self, request):
        """
        Получает IP адрес клиента с учетом прокси
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _unauthorized_response(self, message):
        """
        Возвращает ответ об ошибке аутентификации
        """
        return JsonResponse({
            'error': 'Authentication failed',
            'message': message
        }, status=401)


# Декораторы для защиты API эндпоинтов

def api_token_required(permission_level=None):
    """
    Декоратор для проверки API токена
    
    Args:
        permission_level: Минимальный уровень доступа (read_only, read_write, admin)
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Проверяем наличие аутентификации
            if not getattr(request, 'api_authenticated', False):
                return JsonResponse({
                    'error': 'Authentication required',
                    'message': 'API токен обязателен для этого эндпоинта'
                }, status=401)
            
            # Проверяем уровень доступа, если указан
            if permission_level:
                api_token = getattr(request, 'api_token', None)
                if not api_token or not _check_permission(api_token, permission_level):
                    return JsonResponse({
                        'error': 'Insufficient permissions',
                        'message': f'Требуется уровень доступа: {permission_level}'
                    }, status=403)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def require_read_access(view_func):
    """Декоратор для эндпоинтов, требующих доступ на чтение"""
    return api_token_required('read_only')(view_func)


def require_write_access(view_func):
    """Декоратор для эндпоинтов, требующих доступ на запись"""
    return api_token_required('read_write')(view_func)


def require_admin_access(view_func):
    """Декоратор для эндпоинтов, требующих административный доступ"""
    return api_token_required('admin')(view_func)


def _check_permission(api_token, required_permission):
    """
    Проверяет, имеет ли токен необходимые права доступа
    """
    permission_hierarchy = {
        'read_only': 1,
        'read_write': 2,
        'admin': 3
    }
    
    token_level = permission_hierarchy.get(api_token.permissions, 0)
    required_level = permission_hierarchy.get(required_permission, 0)
    
    return token_level >= required_level


def authenticate_api_token(request):
    """
    Утилита для ручной аутентификации API токена в view
    Возвращает (api_token, error_response)
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header:
        return None, JsonResponse({
            'error': 'Authentication required',
            'message': 'Отсутствует заголовок Authorization'
        }, status=401)
    
    # Извлекаем токен
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() not in ['bearer', 'token']:
        return None, JsonResponse({
            'error': 'Invalid authentication format',
            'message': 'Используйте формат: Bearer <token>'
        }, status=401)
    
    token = parts[1]
    
    # Ищем и проверяем токен
    try:
        prefix = token[:8]
        api_tokens = APIToken.objects.filter(prefix=prefix, is_active=True)
        
        for api_token in api_tokens:
            if api_token.verify_token(token):
                if not api_token.is_valid():
                    break
                
                # Проверяем IP
                client_ip = get_client_ip(request)
                if not api_token.check_ip_access(client_ip):
                    return None, JsonResponse({
                        'error': 'Access denied',
                        'message': 'Доступ с вашего IP адреса запрещен'
                    }, status=403)
                
                # Обновляем время использования
                api_token.update_last_used()
                return api_token, None
        
        return None, JsonResponse({
            'error': 'Invalid token',
            'message': 'Недействительный токен'
        }, status=401)
        
    except Exception as e:
        logger.error(f"Error in authenticate_api_token: {str(e)}")
        return None, JsonResponse({
            'error': 'Authentication error',
            'message': 'Ошибка при проверке токена'
        }, status=500)


def get_client_ip(request):
    """Утилита для получения IP адреса клиента"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip 