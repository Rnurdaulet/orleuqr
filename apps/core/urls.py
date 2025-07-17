from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = 'api'

# DRF Router
router = DefaultRouter()
router.register(r'groups', api_views.MyGroupsViewSet, basename='groups')

urlpatterns = [
    # Базовые API эндпоинты
    path('health/', api_views.api_health_check, name='health_check'),
    
    # DRF endpoints
    path('', include(router.urls)),
    
    # CRUD API для управления группами через код
    path('crud/', include('apps.groups.api_urls', namespace='groups_crud')),
] 