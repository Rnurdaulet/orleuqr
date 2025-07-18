from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.groups.models import Group, Session
from apps.participants.models import PersonProfile
import uuid
from datetime import time, datetime


class ListenerSerializer(serializers.Serializer):
    """Сериализатор для участников в формате miniresponse.json"""
    iin = serializers.CharField(max_length=12)
    surname = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField(required=False, allow_blank=True)


class SessionSerializer(serializers.ModelSerializer):
    """Сериализатор для сессий группы"""
    
    class Meta:
        model = Session
        fields = [
            'date', 'entry_start', 'entry_end', 'exit_start', 'exit_end',
            'qr_token_entry', 'qr_token_exit'
        ]
        extra_kwargs = {
            'qr_token_entry': {'read_only': True},
            'qr_token_exit': {'read_only': True},
        }
    
    def to_representation(self, instance):
        """Исключаем поля выхода, если группа не отслеживает выход"""
        ret = super().to_representation(instance)
        
        # Если группа не отслеживает выход, удаляем соответствующие поля
        if not instance.group.track_exit:
            ret.pop('exit_start', None)
            ret.pop('exit_end', None)
            ret.pop('qr_token_exit', None)
            
        return ret


class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор для группы в ТОЧНОМ формате miniresponse.json"""
    
    # Поля в точном соответствии с miniresponse.json
    groupId = serializers.IntegerField(source='external_id', required=False)
    groupUnique = serializers.CharField(source='code', max_length=10)
    courseName = serializers.CharField(source='course_name')
    supervisorName = serializers.CharField(source='supervisor_name')
    supervisorIIN = serializers.CharField(source='supervisor_iin', max_length=12)
    # Используем DateField вместо DateTimeField так как в модели это DateField
    startingDate = serializers.DateField(source='start_date')
    endingDate = serializers.DateField(source='end_date')
    
    # Участники в точном формате JSON
    listenersList = ListenerSerializer(many=True, required=False)
    
    # Даты сессий в точном формате JSON
    daysforAttendence = serializers.ListField(
        child=serializers.DateTimeField(),
        required=False
    )
    
    class Meta:
        model = Group
        fields = [
            'groupId', 'groupUnique', 'courseName', 'supervisorName', 'supervisorIIN',
            'startingDate', 'endingDate', 'listenersList', 'daysforAttendence'
        ]
        extra_kwargs = {
            'groupUnique': {'validators': []},  # Убираем стандартную валидацию
        }
    
    def validate_groupUnique(self, value):
        """Проверяем уникальность кода группы"""
        if self.instance and self.instance.code == value:
            return value
        
        if Group.objects.filter(code=value).exists():
            raise serializers.ValidationError(_("Группа с таким кодом уже существует"))
        return value
    
    def to_representation(self, instance):
        """Преобразуем модель в JSON формат"""
        # Получаем базовое представление
        ret = super().to_representation(instance)
        
        # Добавляем участников в формате listenersList
        listeners = []
        for participant in instance.participants.all():
            # Разбиваем full_name на surname и name
            name_parts = participant.full_name.split(' ', 1)
            surname = name_parts[0] if name_parts else ''
            name = name_parts[1] if len(name_parts) > 1 else ''
            
            listeners.append({
                'iin': participant.iin,
                'surname': surname,
                'name': name,
                'email': participant.email or ''
            })
        ret['listenersList'] = listeners
        
        # Добавляем даты сессий в формате daysforAttendence
        days = []
        for session in instance.sessions.all():
            # Форматируем дату как в JSON файле
            days.append(session.date.strftime('%Y-%m-%dT00:00:00'))
        ret['daysforAttendence'] = days
        
        # Форматируем даты в формате ISO с T00:00:00
        # Исправляем обработку дат - теперь правильно форматируем date объекты
        if 'startingDate' in ret and ret['startingDate']:
            if isinstance(ret['startingDate'], str):
                # Если уже строка, просто добавляем время
                ret['startingDate'] = f"{ret['startingDate']}T00:00:00"
            else:
                # Если объект date, конвертируем в строку
                ret['startingDate'] = f"{ret['startingDate']}T00:00:00"
                
        if 'endingDate' in ret and ret['endingDate']:
            if isinstance(ret['endingDate'], str):
                # Если уже строка, просто добавляем время
                ret['endingDate'] = f"{ret['endingDate']}T00:00:00"
            else:
                # Если объект date, конвертируем в строку
                ret['endingDate'] = f"{ret['endingDate']}T00:00:00"
            
        return ret
    
    def create(self, validated_data):
        """Создание группы в формате miniresponse.json"""
        listeners_data = validated_data.pop('listenersList', [])
        days_data = validated_data.pop('daysforAttendence', [])
        
        # Создаем группу
        group = Group.objects.create(**validated_data)
        
        # Создаем/получаем тренера (руководителя группы)
        if validated_data.get('supervisor_iin'):
            trainer, _ = PersonProfile.objects.get_or_create(
                iin=validated_data['supervisor_iin'],
                defaults={
                    'full_name': validated_data.get('supervisor_name', ''),
                    'role': PersonProfile.Role.TRAINER
                }
            )
            group.trainers.add(trainer)
        
        # Создаем/получаем участников
        for listener_data in listeners_data:
            full_name = f"{listener_data.get('surname', '')} {listener_data.get('name', '')}".strip()
            participant, _ = PersonProfile.objects.get_or_create(
                iin=listener_data['iin'],
                defaults={
                    'full_name': full_name,
                    'email': listener_data.get('email', ''),
                    'role': PersonProfile.Role.PARTICIPANT
                }
            )
            group.participants.add(participant)
        
        # Создаем сессии из daysforAttendence
        for day_str in days_data:
            # Парсим дату из формата "2025-07-11T00:00:00" или просто строку даты
            if isinstance(day_str, str):
                date_only = day_str.split('T')[0]
            elif isinstance(day_str, datetime):
                date_only = day_str.date()
            else:
                date_only = day_str
                
            Session.objects.get_or_create(
                group=group,
                date=date_only,
                defaults={
                    'entry_start': time(hour=9),
                    'entry_end': time(hour=10),
                    'exit_start': time(hour=17),
                    'exit_end': time(hour=18),
                    'qr_token_entry': uuid.uuid4(),
                    'qr_token_exit': uuid.uuid4() if group.track_exit else None,
                }
            )
        
        return group
    
    def update(self, instance, validated_data):
        """Обновление группы в формате miniresponse.json"""
        listeners_data = validated_data.pop('listenersList', None)
        days_data = validated_data.pop('daysforAttendence', None)
        
        # Обновляем основные поля группы
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Обновляем участников если данные переданы
        if listeners_data is not None:
            instance.participants.clear()
            for listener_data in listeners_data:
                full_name = f"{listener_data.get('surname', '')} {listener_data.get('name', '')}".strip()
                participant, _ = PersonProfile.objects.get_or_create(
                    iin=listener_data['iin'],
                    defaults={
                        'full_name': full_name,
                        'email': listener_data.get('email', ''),
                        'role': PersonProfile.Role.PARTICIPANT
                    }
                )
                instance.participants.add(participant)
        
        # Обновляем сессии если даты переданы
        if days_data is not None:
            # Удаляем старые сессии
            instance.sessions.all().delete()
            # Создаем новые
            for day_str in days_data:
                # Правильная обработка дат
                if isinstance(day_str, str):
                    date_only = day_str.split('T')[0]
                elif isinstance(day_str, datetime):
                    date_only = day_str.date()
                else:
                    date_only = day_str
                    
                Session.objects.get_or_create(
                    group=instance,  # Исправлено: используем instance вместо group
                    date=date_only,
                    defaults={
                        'entry_start': time(hour=9),
                        'entry_end': time(hour=10),
                        'exit_start': time(hour=17),
                        'exit_end': time(hour=18),
                        'qr_token_entry': uuid.uuid4(),
                        'qr_token_exit': uuid.uuid4() if instance.track_exit else None,
                    }
                )
        
        return instance


class GroupListSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для списка групп"""
    
    groupId = serializers.IntegerField(source='external_id', read_only=True)
    groupUnique = serializers.CharField(source='code', read_only=True)
    courseName = serializers.CharField(source='course_name', read_only=True)
    supervisorName = serializers.CharField(source='supervisor_name', read_only=True)
    startingDate = serializers.DateField(source='start_date', read_only=True)
    endingDate = serializers.DateField(source='end_date', read_only=True)
    participantsCount = serializers.SerializerMethodField()
    trainersCount = serializers.SerializerMethodField()
    trackExit = serializers.BooleanField(source='track_exit', read_only=True)
    
    class Meta:
        model = Group
        fields = [
            'groupId', 'groupUnique', 'courseName', 'supervisorName',
            'startingDate', 'endingDate', 'participantsCount', 'trainersCount', 'trackExit'
        ]
    
    def get_participantsCount(self, obj):
        """Количество участников в группе"""
        return obj.participants.count()
    
    def get_trainersCount(self, obj):
        """Количество тренеров в группе"""
        return obj.trainers.count() 