# API Токены для доверенных сервисов

Система API токенов позволяет доверенным сервисам обращаться к API проекта без использования пользовательской аутентификации через Keycloak.

## Особенности

- **Безопасность**: Токены хешируются с использованием SHA-256
- **Уровни доступа**: read_only, read_write, admin
- **IP ограничения**: Возможность ограничить доступ по IP адресам
- **Срок действия**: Токены могут иметь ограниченный срок действия
- **Отслеживание**: Логирование времени последнего использования

## Управление токенами

### 1. Через админку Django

Перейдите в `/admin/core/apitoken/` для управления токенами через веб-интерфейс.

### 2. Через management команду

#### Создание токена
```bash
# Базовый токен с правами только на чтение
python manage.py manage_api_tokens create "Мой Сервис"

# Токен с правами на запись
python manage.py manage_api_tokens create "Внешний API" --permissions read_write

# Токен с административными правами и ограничением по IP
python manage.py manage_api_tokens create "Админский сервис" \
    --permissions admin \
    --ip-whitelist "192.168.1.100,10.0.0.5" \
    --description "Сервис для административных операций"

# Токен с ограниченным сроком действия (30 дней)
python manage.py manage_api_tokens create "Временный сервис" \
    --expires-days 30
```

#### Просмотр токенов
```bash
# Все токены
python manage.py manage_api_tokens list

# Только активные токены
python manage.py manage_api_tokens list --active-only
```

#### Управление токенами
```bash
# Информация о токене
python manage.py manage_api_tokens info 1

# Деактивация токена
python manage.py manage_api_tokens deactivate 1

# Активация токена
python manage.py manage_api_tokens activate 1

# Удаление токена
python manage.py manage_api_tokens delete 1 --confirm
```

### 3. Через API (только для admin токенов)

#### Создание токена
```bash
curl -X POST http://localhost:8000/api/tokens/create/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Новый сервис",
    "permissions": "read_write",
    "description": "Описание сервиса",
    "expires_days": 60
  }'
```

#### Список токенов
```bash
curl http://localhost:8000/api/tokens/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Использование API

### Аутентификация

Добавьте заголовок Authorization ко всем API запросам:

```
Authorization: Bearer YOUR_API_TOKEN
```

### Доступные эндпоинты

#### 1. Проверка работоспособности (read_only)
```bash
curl http://localhost:8000/api/health/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Ответ:
```json
{
  "status": "healthy",
  "message": "API работает корректно",
  "authenticated_service": "Мой Сервис",
  "permissions": "read_only",
  "timestamp": "2025-01-15T12:30:00.000Z"
}
```

#### 2. Список участников (read_only)
```bash
curl "http://localhost:8000/api/participants/?page=1&per_page=10&role=participant" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Параметры:
- `page`: Номер страницы (по умолчанию: 1)
- `per_page`: Записей на странице (максимум 100, по умолчанию: 20)
- `role`: Фильтр по роли (participant/trainer)
- `search`: Поиск по имени, email или ИИН

#### 3. Список групп (read_only)
```bash
curl http://localhost:8000/api/groups/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 4. Отметка посещаемости (read_write)
```bash
curl -X POST http://localhost:8000/api/attendance/mark/ \
  -H "Authorization: Bearer YOUR_WRITE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 123,
    "participant_id": 456,
    "mode": "entry"
  }'
```

Параметры:
- `session_id`: ID сессии
- `participant_id`: ID участника
- `mode`: "entry" (вход) или "exit" (выход)

## Уровни доступа

### read_only
- Получение информации об участниках
- Получение информации о группах
- Проверка работоспособности API

### read_write
- Все права read_only
- Отметка посещаемости
- Создание и изменение записей

### admin
- Все права read_write
- Управление API токенами
- Административные операции

## Безопасность

### Рекомендации
1. **Храните токены в безопасном месте** (переменные окружения, секреты)
2. **Используйте минимально необходимые права** доступа
3. **Ограничивайте доступ по IP** при возможности
4. **Устанавливайте срок действия** для временных интеграций
5. **Регулярно ротируйте токены**

### IP ограничения
Токены могут быть ограничены по IP адресам:
```
# Один IP
192.168.1.100

# Несколько IP через запятую
192.168.1.100,10.0.0.5,203.0.113.1
```

### Обработка ошибок

#### 401 Unauthorized
```json
{
  "error": "Authentication failed",
  "message": "Недействительный токен"
}
```

#### 403 Forbidden
```json
{
  "error": "Insufficient permissions",
  "message": "Требуется уровень доступа: read_write"
}
```

#### 404 Not Found
```json
{
  "error": "Session not found", 
  "message": "Сессия с ID 123 не найдена"
}
```

## Примеры интеграции

### Python (requests)
```python
import requests

API_TOKEN = "YOUR_API_TOKEN"
BASE_URL = "http://localhost:8000/api"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Получение участников
response = requests.get(f"{BASE_URL}/participants/", headers=headers)
participants = response.json()

# Отметка посещаемости
attendance_data = {
    "session_id": 123,
    "participant_id": 456,
    "mode": "entry"
}
response = requests.post(
    f"{BASE_URL}/attendance/mark/", 
    json=attendance_data, 
    headers=headers
)
```

### JavaScript (fetch)
```javascript
const API_TOKEN = 'YOUR_API_TOKEN';
const BASE_URL = 'http://localhost:8000/api';

const headers = {
    'Authorization': `Bearer ${API_TOKEN}`,
    'Content-Type': 'application/json'
};

// Получение групп
fetch(`${BASE_URL}/groups/`, { headers })
    .then(response => response.json())
    .then(data => console.log(data));

// Отметка посещаемости
fetch(`${BASE_URL}/attendance/mark/`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
        session_id: 123,
        participant_id: 456,
        mode: 'entry'
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

### cURL примеры
```bash
# Переменная для удобства
export API_TOKEN="YOUR_API_TOKEN"
export API_URL="http://localhost:8000/api"

# Проверка здоровья
curl "$API_URL/health/" -H "Authorization: Bearer $API_TOKEN"

# Участники с фильтрацией
curl "$API_URL/participants/?role=trainer&search=Иванов" \
  -H "Authorization: Bearer $API_TOKEN"

# Отметка прихода
curl -X POST "$API_URL/attendance/mark/" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_id": 123, "participant_id": 456, "mode": "entry"}'
```

## Мониторинг и логи

Все API запросы логируются с информацией о:
- Использованном токене
- IP адресе клиента
- Времени запроса
- Результате аутентификации

Просмотр логов:
```bash
tail -f logs/django.log | grep "API request authenticated"
``` 