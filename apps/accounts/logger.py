import logging
import os
from django.conf import settings

logger = logging.getLogger('accounts')

# Уровень логирования зависит от DEBUG режима
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# Создаем форматтер для логов
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Добавляем обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Файловое логирование только для WARNING и выше в продакшене
if not settings.DEBUG:
    # Используем папку logs из настроек Django
    log_dir = getattr(settings, 'LOG_DIR', os.path.join(settings.BASE_DIR, 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, 'accounts.log')
    
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler) 