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

# DRF imports
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission
from django.utils.timezone import now


class APITokenPermission(BasePermission):
    """
    Проверка прав доступа через API токены
    """
    def has_permission(self, request, view):
        api_token, error_response = authenticate_api_token(request)
        if error_response:
            return False
        
        # Сохраняем токен в запросе для дальнейшего использования
        request.api_token = api_token
        
        # Для чтения требуются минимальные права
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return api_token.permissions in ['read_only', 'read_write', 'admin']
        
        # Для записи требуются соответствующие права
        return api_token.permissions in ['read_write', 'admin']


class AttendanceSerializer(serializers.ModelSerializer):
    """Сериализатор для посещаемости"""
    arrived_status_display = serializers.CharField(source='get_arrived_status_display', read_only=True)
    left_status_display = serializers.CharField(source='get_left_status_display', read_only=True)
    trust_level_display = serializers.CharField(source='get_trust_level_display', read_only=True)
    marked_entry_by_trainer = serializers.SerializerMethodField()
    marked_exit_by_trainer = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'arrived_at', 'arrived_status', 'arrived_status_display',
            'left_at', 'left_status', 'left_status_display', 
            'trust_level', 'trust_level_display', 'trust_score',
            'marked_entry_by_trainer', 'marked_exit_by_trainer'
        ]
    
    def get_marked_entry_by_trainer(self, obj):
        return bool(obj.marked_entry_by_trainer)
    
    def get_marked_exit_by_trainer(self, obj):
        return bool(obj.marked_exit_by_trainer)


class SessionSerializer(serializers.ModelSerializer):
    """Сериализатор для сессий"""
    is_today = serializers.SerializerMethodField()
    attendance = serializers.SerializerMethodField()
    
    class Meta:
        model = Session
        fields = ['id', 'date', 'is_today', 'attendance']
    
    def get_is_today(self, obj):
        return obj.date == now().date()
    
    def get_attendance(self, obj):
        # Получаем участника из контекста
        participant = self.context.get('participant')
        if not participant:
            return None
        
        try:
            attendance = obj.attendances.get(profile=participant)
            return AttendanceSerializer(attendance).data
        except Attendance.DoesNotExist:
            return None


class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор для групп"""
    sessions_count = serializers.SerializerMethodField()
    sessions = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = [
            'id', 'code', 'course_name', 'start_date', 'end_date',
            'sessions_count', 'sessions'
        ]
    
    def get_sessions_count(self, obj):
        return obj.sessions.count()
    
    def get_sessions(self, obj):
        participant = self.context.get('participant')
        sessions = obj.sessions.all().order_by('date')
        return SessionSerializer(
            sessions, 
            many=True, 
            context={'participant': participant}
        ).data


class MyGroupsPagination(PageNumberPagination):
    """Пагинация для API групп"""
    page_size = 10
    page_size_query_param = 'per_page'
    max_page_size = 100


class MyGroupsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для получения групп участника с посещаемостью
    """
    serializer_class = GroupSerializer
    permission_classes = [APITokenPermission]
    pagination_class = MyGroupsPagination
    
    def get_queryset(self):
        # Для демонстрации: берем участника из параметра запроса
        participant_iin = self.request.query_params.get('participant_iin')
        if not participant_iin:
            return Group.objects.none()
        
        try:
            participant = PersonProfile.objects.get(
                iin=participant_iin, 
                role=PersonProfile.Role.PARTICIPANT
            )
        except PersonProfile.DoesNotExist:
            return Group.objects.none()
        
        # Сохраняем участника для использования в сериализаторе
        self.participant = participant
        
        # Фильтруем группы участника
        today = now().date()
        return Group.objects.filter(
            participants=participant,
            end_date__gte=today
        ).prefetch_related(
            'sessions',
            'sessions__attendances',
            'sessions__attendances__profile',
            'sessions__attendances__marked_entry_by_trainer',
            'sessions__attendances__marked_exit_by_trainer'
        ).order_by('start_date')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['participant'] = getattr(self, 'participant', None)
        return context
    
    @action(detail=False, methods=['get'])
    def my_groups(self, request):
        """
        API endpoint для получения групп участника в формате как в my_groups.html
        """
        participant_iin = request.query_params.get('participant_iin')
        
        # Проверяем наличие обязательного параметра
        if not participant_iin:
            return Response({
                'error': 'Missing required parameter',
                'message': 'Параметр participant_iin обязателен',
                'details': 'Укажите ИИН участника в параметре participant_iin'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем существование участника
        try:
            participant = PersonProfile.objects.get(
                iin=participant_iin, 
                role=PersonProfile.Role.PARTICIPANT
            )
        except PersonProfile.DoesNotExist:
            return Response({
                'error': 'Participant not found',
                'message': f'Участник с ИИН {participant_iin} не найден',
                'details': 'Проверьте правильность ИИН или убедитесь, что профиль имеет роль "Участник"',
                'groups': [],
                'total_groups': 0,
                'pagination': {
                    'page': 1,
                    'per_page': 10,
                    'total_pages': 0,
                    'total_items': 0
                },
                'filter_options': self._get_filter_options()
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Сохраняем участника для сериализатора
        self.participant = participant
        
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            
            # Формируем ответ в нужном формате
            response_data = {
                'groups': paginated_response.data['results'],
                'total_groups': paginated_response.data['count'],
                'pagination': {
                    'page': int(request.query_params.get('page', 1)),
                    'per_page': int(request.query_params.get('per_page', 10)),
                    'total_pages': paginated_response.data['count'] // int(request.query_params.get('per_page', 10)) + 1,
                    'total_items': paginated_response.data['count']
                },
                'filter_options': self._get_filter_options(),
                'participant_info': {
                    'iin': participant.iin,
                    'full_name': participant.full_name,
                    'role': participant.get_role_display()
                }
            }
            
            # Если групп нет, добавляем пояснение
            if paginated_response.data['count'] == 0:
                response_data['message'] = f'У участника {participant.full_name} нет активных групп'
                response_data['details'] = 'Возможно, все группы завершены или участник еще не записан ни в одну группу'
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(queryset, many=True)
        
        response_data = {
            'groups': serializer.data,
            'total_groups': len(serializer.data),
            'pagination': {
                'page': 1,
                'per_page': len(serializer.data) if serializer.data else 10,
                'total_pages': 1 if serializer.data else 0,
                'total_items': len(serializer.data)
            },
            'filter_options': self._get_filter_options(),
            'participant_info': {
                'iin': participant.iin,
                'full_name': participant.full_name,
                'role': participant.get_role_display()
            }
        }
        
        # Если групп нет, добавляем пояснение
        if len(serializer.data) == 0:
            response_data['message'] = f'У участника {participant.full_name} нет активных групп'
            response_data['details'] = 'Возможно, все группы завершены или участник еще не записан ни в одну группу'
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def _get_filter_options(self):
        """Возвращает опции для фильтров"""
        return {
            'arrival_statuses': [
                {'value': 'on_time', 'display': 'Вовремя'},
                {'value': 'too_late', 'display': 'Опоздал'},
                {'value': 'too_early', 'display': 'Рано'},
                {'value': 'by_trainer', 'display': 'Отметка тренером'},
                {'value': 'unknown', 'display': 'Неизвестно'}
            ],
            'trust_levels': [
                {'value': 'trusted', 'display': 'Доверенный'},
                {'value': 'suspicious', 'display': 'Подозрительный'},
                {'value': 'blocked', 'display': 'Заблокирован'},
                {'value': 'manual_by_trainer', 'display': 'Ручная отметка'}
            ]
        }


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