# Тестирование API Groups CRUD

## Быстрый старт

### 1. Запустите сервер
```bash
python manage.py runserver
```

### 2. Создайте API токен
1. Откройте админ панель: http://localhost:8000/admin/
2. Перейдите в раздел "API Tokens" (Core → API tokens)
3. Нажмите "Add API token"
4. Заполните:
   - **Name**: Test Token (или любое другое название)
   - **Permissions**: `read_write` (для полного доступа)
   - **Allowed IPs**: оставьте пустым для доступа с любого IP
5. Сохраните и скопируйте сгенерированный токен

### 3. Настройте токен для тестов
Установите переменную окружения:
```bash
export API_TOKEN=your-copied-token-here
```

Или измените токен прямо в файле `test_groups_api.py`:
```python
API_TOKEN = "your-copied-token-here"
```

### 4. Запустите тесты
```bash
python test_groups_api.py
```

## Ручное тестирование

### Создание группы
```bash
curl -X POST http://localhost:8000/api/crud/groups/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "groupId": 12345,
    "groupUnique": "TEST001",
    "courseName": "Тестовый курс",
    "supervisorName": "Иванов Иван Иванович",
    "supervisorIIN": "123456789012",
    "startingDate": "2024-01-01T00:00:00",
    "endingDate": "2024-01-31T00:00:00",
    "listenersList": [
      {
        "iin": "987654321098",
        "surname": "ПЕТРОВ",
        "name": "ПЕТР",
        "email": "petrov@example.com"
      }
    ],
    "daysforAttendence": [
      "2024-01-01T00:00:00",
      "2024-01-02T00:00:00"
    ]
  }'
```

### Получение группы
```bash
curl -X GET http://localhost:8000/api/crud/groups/TEST001/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Обновление участников
```bash
curl -X PATCH http://localhost:8000/api/crud/groups/TEST001/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "listenersList": [
      {
        "iin": "987654321098",
        "surname": "ПЕТРОВ",
        "name": "ПЕТР",
        "email": "petrov@example.com"
      },
      {
        "iin": "111111111111",
        "surname": "НОВЫЙ",
        "name": "УЧАСТНИК",
        "email": "new@example.com"
      }
    ]
  }'
```

## Возможные ошибки

### 401 Unauthorized
- Неправильный токен
- Токен не передан в заголовке
- Токен истек или неактивен

**Решение**: Проверьте токен в админ панели, убедитесь что он активен и правильно передается в заголовке `Authorization: Bearer <token>`

### 403 Forbidden
- Недостаточно прав у токена
- IP адрес заблокирован

**Решение**: Убедитесь что токен имеет права `read_write` для записи или `read_only` для чтения

### 404 Not Found
- Группа с указанным кодом не существует
- Неправильный URL

**Решение**: Проверьте код группы и URL эндпоинта

## Проверка статуса API

Быстрая проверка что API работает:
```bash
curl -X GET http://localhost:8000/api/crud/groups/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Должен вернуть список групп и статус 200.

## Тестирование обработки ошибок

API всегда возвращает ошибки в JSON формате, даже при статусе 500:

### Тест ошибки 500
```bash
curl -X GET http://localhost:8000/api/crud/groups/test-error/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Ответ будет в JSON:
```json
{
  "error": true,
  "status_code": 500,
  "message": "Внутренняя ошибка сервера", 
  "details": "Тестовая ошибка для проверки JSON ответа",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Тест ошибки 404
```bash
curl -X GET http://localhost:8000/api/crud/groups/NONEXISTENT/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Тестовый скрипт `test_groups_api.py` автоматически проверяет:
- ✅ Все ошибки возвращаются в JSON формате
- ✅ Правильные коды статусов
- ✅ Корректная структура ошибок
- ✅ Обработка различных типов исключений 