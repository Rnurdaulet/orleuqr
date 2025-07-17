import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import DatabaseError, IntegrityError

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для API.
    Всегда возвращает JSON ответ, даже при серверных ошибках.
    """
    
    # Получаем стандартный ответ от DRF
    response = exception_handler(exc, context)
    
    if response is not None:
        # Если DRF обработал исключение, форматируем ответ
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
            'message': 'Ошибка выполнения запроса',
            'details': response.data
        }
        
        # Добавляем человекочитаемые сообщения для распространенных ошибок
        if response.status_code == 400:
            custom_response_data['message'] = 'Некорректные данные в запросе'
        elif response.status_code == 401:
            custom_response_data['message'] = 'Ошибка аутентификации'
        elif response.status_code == 403:
            custom_response_data['message'] = 'Доступ запрещен'
        elif response.status_code == 404:
            custom_response_data['message'] = 'Ресурс не найден'
        elif response.status_code == 405:
            custom_response_data['message'] = 'Метод не разрешен'
        elif response.status_code == 429:
            custom_response_data['message'] = 'Превышен лимит запросов'
        
        response.data = custom_response_data
        return response
    
    # Обрабатываем исключения, которые DRF не поймал
    error_message = 'Внутренняя ошибка сервера'
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    details = None
    
    try:
        if isinstance(exc, Http404):
            error_message = 'Ресурс не найден'
            status_code = status.HTTP_404_NOT_FOUND
            details = str(exc)
            
        elif isinstance(exc, PermissionDenied):
            error_message = 'Доступ запрещен'
            status_code = status.HTTP_403_FORBIDDEN
            details = str(exc)
            
        elif isinstance(exc, ValidationError):
            error_message = 'Ошибка валидации данных'
            status_code = status.HTTP_400_BAD_REQUEST
            details = exc.message_dict if hasattr(exc, 'message_dict') else str(exc)
            
        elif isinstance(exc, IntegrityError):
            error_message = 'Ошибка целостности данных'
            status_code = status.HTTP_400_BAD_REQUEST
            details = 'Нарушение ограничений базы данных'
            
        elif isinstance(exc, DatabaseError):
            error_message = 'Ошибка базы данных'
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            details = 'Проблема с подключением к базе данных'
            
        else:
            # Логируем неизвестные исключения
            logger.error(f"Unhandled exception in API: {type(exc).__name__}: {str(exc)}", exc_info=True)
            details = str(exc) if str(exc) else f"{type(exc).__name__}"
            
    except Exception as e:
        # Если даже обработка исключения упала
        logger.error(f"Error in exception handler: {e}", exc_info=True)
        details = "Критическая ошибка сервера"
    
    # Создаем JSON ответ
    custom_response_data = {
        'error': True,
        'status_code': status_code,
        'message': error_message,
        'details': details,
        'timestamp': None
    }
    
    # Добавляем временную метку
    try:
        from django.utils import timezone
        custom_response_data['timestamp'] = timezone.now().isoformat()
    except:
        pass
    
    return Response(custom_response_data, status=status_code) 