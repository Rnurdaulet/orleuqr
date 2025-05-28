from __future__ import absolute_import, unicode_literals
import os
import sys  # Добавляем sys для обхода конфликтов


# Добавляем путь к проекту в sys.path, чтобы Python искал в нужном месте
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from celery import Celery  # Теперь импорт не конфликтует

# Устанавливаем переменную окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'platformppi.settings')

app = Celery('platformppi')

# Используем настройки из settings.py с префиксом CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматический поиск тасков во всех приложениях Django
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
