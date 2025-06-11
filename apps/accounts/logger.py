import logging

logger = logging.getLogger('accounts')
logger.setLevel(logging.DEBUG)

# Создаем форматтер для логов
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Добавляем обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Добавляем обработчик для записи в файл
file_handler = logging.FileHandler('accounts.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler) 