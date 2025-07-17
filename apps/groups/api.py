import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from apps.groups.models import Group
from apps.groups.serializers import GroupSerializer, GroupListSerializer

logger = logging.getLogger(__name__)





class GroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операций с группами через код.
    Формат данных точно как в miniresponse.json.
    Все операции (группы, участники, сессии) управляются через один API.
    """
    queryset = Group.objects.all()
    permission_classes = []  # Используем кастомную авторизацию через декораторы
    lookup_field = 'code'
    lookup_url_kwarg = 'code'
    
    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от действия"""
        if self.action == 'list':
            return GroupListSerializer
        return GroupSerializer
    
    def get_queryset(self):
        """Получаем QuerySet с предзагруженными связанными объектами"""
        return Group.objects.prefetch_related(
            'participants',
            'trainers', 
            'sessions'
        ).select_related().order_by('-start_date')
    
    def list(self, request, *args, **kwargs):
        """
        GET /api/crud/groups/
        Получить список всех групп (упрощенный формат)
        """
        groups = self.get_queryset()
        serializer = self.get_serializer(groups, many=True)
        return Response({
            'count': groups.count(),
            'results': serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/crud/groups/{code}/
        Получить подробную информацию о группе по коду в формате miniresponse.json
        """
        group = get_object_or_404(Group, code=kwargs.get('code'))
        serializer = self.get_serializer(group)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        POST /api/crud/groups/
        Создать новую группу в формате miniresponse.json
        
        Пример данных:
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
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save()
            return Response(
                GroupSerializer(group).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """
        PUT /api/crud/groups/{code}/
        Полное обновление группы по коду в формате miniresponse.json
        """
        group = get_object_or_404(Group, code=kwargs.get('code'))
        serializer = self.get_serializer(group, data=request.data)
        if serializer.is_valid():
            group = serializer.save()
            return Response(GroupSerializer(group).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /api/crud/groups/{code}/
        Частичное обновление группы по коду в формате miniresponse.json
        """
        group = get_object_or_404(Group, code=kwargs.get('code'))
        serializer = self.get_serializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            group = serializer.save()
            return Response(GroupSerializer(group).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/crud/groups/{code}/
        Удалить группу по коду
        """
        group = get_object_or_404(Group, code=kwargs.get('code'))
        group.delete()
        return Response(
            {'message': _('Группа успешно удалена')},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=False, methods=['get'], url_path='test-error')
    def test_error(self, request):
        """
        GET /api/crud/groups/test-error/
        Тестовый endpoint для проверки обработки ошибок 500.
        Намеренно вызывает исключение для проверки JSON ответа.
        """
        error_type = request.query_params.get('type', 'generic')
        
        if error_type == 'division':
            # Ошибка деления на ноль
            result = 1 / 0
        elif error_type == 'attribute':
            # Ошибка атрибута
            obj = None
            obj.nonexistent_method()
        elif error_type == 'database':
            # Ошибка базы данных
            Group.objects.raw("SELECT * FROM nonexistent_table")
        elif error_type == 'key':
            # Ошибка ключа
            data = {}
            value = data['nonexistent_key']
        else:
            # Общая ошибка
            raise Exception("Тестовая ошибка для проверки JSON ответа")
        
        return Response({'message': 'Этот ответ не должен быть возвращен'}) 