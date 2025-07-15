from django.shortcuts import render
from django.db.models import Count
from django.utils import timezone
from datetime import datetime, timedelta
from apps.groups.models import Group, Session
from apps.participants.models import PersonProfile
from apps.attendance.models import Attendance


def home_view(request):
    """
    Главная страница с выбором шаблона в зависимости от роли пользователя
    """
    user_profile = getattr(request, 'user_profile', None)
    
    # Для неавторизованных пользователей - лэндинг
    if not user_profile:
        return render(request, 'index/landing.html')
    
    # Общие данные для всех авторизованных пользователей
    context = {
        'user_profile': user_profile,
    }
    
    # Для участников
    if user_profile.role == 'participant':
        # Статистика для участника
        today = timezone.now().date()
        my_visits_today = Attendance.objects.filter(
            profile=user_profile,
            created__date=today
        ).count()
        
        my_groups_count = user_profile.groups.count()
        
        context.update({
            'my_visits_today': my_visits_today,
            'my_groups_count': my_groups_count,
        })
        
        return render(request, 'index/participant.html', context)
    
    # Для тренеров и администраторов
    else:
        # Статистика для тренера/админа
        today = timezone.now().date()
        
        # Всего групп (для тренера - только его группы)
        if user_profile.role == 'trainer':
            total_groups = user_profile.trainer_groups.count()
        else:
            total_groups = Group.objects.count()
        
        # Всего участников
        total_participants = PersonProfile.objects.filter(role='participant').count()
        
        # Посещения сегодня
        today_visits = Attendance.objects.filter(
            created__date=today
        ).count()
        
        # Активные сессии (сегодня)
        active_sessions = Session.objects.filter(
            date=today
        ).count()
        
        context.update({
            'total_groups': total_groups,
            'total_participants': total_participants,
            'today_visits': today_visits,
            'active_sessions': active_sessions,
        })
        
        return render(request, 'index/trainer.html', context)
