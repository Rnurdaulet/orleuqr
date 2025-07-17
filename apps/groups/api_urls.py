from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import GroupViewSet

# Создаем роутер для автоматического создания URL patterns
router = DefaultRouter()
router.register(r'groups', GroupViewSet, basename='group')

app_name = 'groups_api'

urlpatterns = [
    # API маршруты
    path('', include(router.urls)),
]

# Дополнительная информация о доступных маршрутах:
"""
API Endpoints для работы с группами через код в формате miniresponse.json:

Основные CRUD операции:
- GET    /api/crud/groups/                     - список всех групп
- POST   /api/crud/groups/                     - создать новую группу  
- GET    /api/crud/groups/{code}/              - получить группу по коду
- PUT    /api/crud/groups/{code}/              - полное обновление группы
- PATCH  /api/crud/groups/{code}/              - частичное обновление группы
- DELETE /api/crud/groups/{code}/              - удалить группу

ФОРМАТ ДАННЫХ точно как в miniresponse.json:

1. Создать группу:
POST /api/crud/groups/
{
    "groupId": 14462,
    "groupUnique": "26EB9T",
    "courseName": "«Бастауыш сынып оқушыларының зерттеушілік»",
    "supervisorName": "Ильясова Гульзира",
    "supervisorIIN": "831212401667",
    "startingDate": "2025-07-11T00:00:00",
    "endingDate": "2025-07-18T00:00:00",
    "listenersList": [
        {
            "iin": "841105401171",
            "surname": "АЛИМКУЛОВА",
            "name": "КУНДУЗАЙ",
            "email": "alimkulova_k@mail.ru"
        }
    ],
    "daysforAttendence": [
        "2025-07-11T00:00:00",
        "2025-07-12T00:00:00"
    ]
}

2. Получить группу:
GET /api/crud/groups/26EB9T/

3. Обновить группу (можно обновлять участников и сессии через listenersList и daysforAttendence):
PATCH /api/crud/groups/26EB9T/
{
    "courseName": "Обновленное название",
    "listenersList": [
        {
            "iin": "111111111111",
            "surname": "НОВЫЙ",
            "name": "УЧАСТНИК",
            "email": "new@example.com"
        }
    ]
}

ОСОБЕННОСТИ:
- Все поля точно как в miniresponse.json
- Участники в формате surname + name (не full_name)
- Даты в формате "2025-07-11T00:00:00"
- Управление участниками и сессиями через основной CRUD
- Тренер создается автоматически из supervisorName/supervisorIIN
""" 