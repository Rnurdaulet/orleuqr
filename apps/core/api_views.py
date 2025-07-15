import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
from .api_auth import (
    require_read_access, 
    require_write_access, 
    require_admin_access,
    authenticate_api_token
)
from .models import APIToken
from apps.participants.models import PersonProfile
from apps.groups.models import Group, Session
from apps.attendance.models import Attendance
from django.db import models
from django.utils import timezone
from datetime import timedelta


@require_http_methods(["GET"])
@require_read_access
def api_health_check(request):
    """
    Проверка работоспособности API
    Требует минимальные права доступа (read_only)
    """
    api_token = getattr(request, 'api_token', None)
    
    return JsonResponse({
        'status': 'healthy',
        'message': 'API работает корректно',
        'authenticated_service': api_token.name if api_token else None,
        'permissions': api_token.permissions if api_token else None,
        'timestamp': timezone.now().isoformat()
    })

    """
    API для управления токенами (только для администраторов)
    """
    
    def dispatch(self, request, *args, **kwargs):
        # Проверяем аутентификацию
        api_token, error_response = authenticate_api_token(request)
        if error_response:
            return error_response
        
        # Проверяем права администратора
        if api_token.permissions != 'admin':
            return JsonResponse({
                'error': 'Insufficient permissions',
                'message': 'Требуются права администратора'
            }, status=403)
        
        request.api_token = api_token
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        """Создание нового API токена"""
        try:
            data = json.loads(request.body)
            
            name = data.get('name')
            if not name:
                return JsonResponse({
                    'error': 'Missing required field',
                    'message': 'Поле name обязательно'
                }, status=400)
            
            permissions = data.get('permissions', 'read_only')
            if permissions not in ['read_only', 'read_write', 'admin']:
                return JsonResponse({
                    'error': 'Invalid permissions',
                    'message': 'Допустимые значения: read_only, read_write, admin'
                }, status=400)
            
            # Дополнительные параметры
            token_params = {
                'permissions': permissions,
                'description': data.get('description', ''),
                'ip_whitelist': data.get('ip_whitelist', '')
            }
            
            # Срок действия
            if data.get('expires_days'):
                token_params['expires_at'] = timezone.now() + timedelta(days=data['expires_days'])
            
            api_token, token = APIToken.create_token(name, **token_params)
            
            return JsonResponse({
                'success': True,
                'message': 'Токен успешно создан',
                'token': {
                    'id': api_token.id,
                    'name': api_token.name,
                    'permissions': api_token.permissions,
                    'token': token,  # Возвращаем токен только при создании
                    'expires_at': api_token.expires_at.isoformat() if api_token.expires_at else None
                }
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON',
                'message': 'Некорректный формат JSON'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': 'Internal server error',
                'message': str(e)
            }, status=500)
    
    def delete(self, request, token_id):
        """Удаление API токена"""
        try:
            token = APIToken.objects.get(id=token_id)
            token_name = token.name
            token.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Токен {token_name} успешно удален'
            })
            
        except APIToken.DoesNotExist:
            return JsonResponse({
                'error': 'Token not found',
                'message': f'Токен с ID {token_id} не найден'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'error': 'Internal server error',
                'message': str(e)
            }, status=500) 