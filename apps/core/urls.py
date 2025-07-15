from django.urls import path
from . import api_views

app_name = 'api'

urlpatterns = [
    # Базовые API эндпоинты
    path('health/', api_views.api_health_check, name='health_check'),
] 