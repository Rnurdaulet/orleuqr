# API Токены - Документация по использованию

## Обзор

Этот документ описывает использование API токенов для доступа к REST API системы учета посещаемости.

## Аутентификация

Все API запросы должны включать HTTP заголовок авторизации:
```
Authorization: Bearer YOUR_API_TOKEN
```

## Уровни доступа

1. **read_only** - только чтение данных
2. **read_write** - чтение и запись данных  
3. **admin** - полный доступ + управление токенами

## Управление токенами

### Создание токена (только для администраторов)

```bash
curl -X POST http://localhost:8000/api/tokens/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-service",
    "permissions": "read_only",
    "description": "Токен для чтения данных",
    "expires_days": 30
  }'
```

### Удаление токена

```bash
curl -X DELETE http://localhost:8000/api/tokens/TOKEN_ID/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

## Проверка состояния API

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/health/
```

## API Групп и Посещаемости

### Получение групп участника

**Endpoint:** `GET /api/groups/my_groups/`

**Параметры запроса:**
- `participant_iin` (обязательный) - ИИН участника
- `page` (опциональный) - номер страницы (по умолчанию: 1)
- `per_page` (опциональный) - количество элементов на странице (по умолчанию: 10, максимум: 100)

**Пример запроса:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/groups/my_groups/?participant_iin=123456789012&page=1&per_page=5"
```

**Пример ответа:**
```json
{
  "groups": [
    {
      "id": 1,
      "code": "GROUP001",
      "course_name": "Веб-разработка",
      "start_date": "2024-01-15",
      "end_date": "2024-06-15",
      "sessions_count": 48,
      "sessions": [
        {
          "id": 101,
          "date": "2024-01-15",
          "is_today": false,
          "attendance": {
            "id": 501,
            "arrived_at": "2024-01-15T09:15:00Z",
            "arrived_status": "on_time",
            "arrived_status_display": "Вовремя",
            "left_at": "2024-01-15T17:45:00Z", 
            "left_status": "on_time",
            "left_status_display": "Вовремя",
            "trust_level": "trusted",
            "trust_level_display": "Доверенный",
            "trust_score": 85,
            "marked_entry_by_trainer": false,
            "marked_exit_by_trainer": true
          }
        },
        {
          "id": 102,
          "date": "2024-01-16",
          "is_today": true,
          "attendance": {
            "id": 502,
            "arrived_at": "2024-01-16T09:35:00Z",
            "arrived_status": "too_late",
            "arrived_status_display": "Опоздал",
            "left_at": null,
            "left_status": null,
            "left_status_display": null,
            "trust_level": "suspicious",
            "trust_level_display": "Подозрительный",
            "trust_score": 65,
            "marked_entry_by_trainer": true,
            "marked_exit_by_trainer": false
          }
        },
        {
          "id": 103,
          "date": "2024-01-17",
          "is_today": false,
          "attendance": null
        }
      ]
    }
  ],
  "total_groups": 1,
  "participant_info": {
    "iin": "123456789012",
    "full_name": "Иванов Иван Иванович",
    "role": "Участник"
  },
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 1,
    "total_items": 1
  },
  "filter_options": {
    "arrival_statuses": [
      {"value": "on_time", "display": "Вовремя"},
      {"value": "too_late", "display": "Опоздал"},
      {"value": "too_early", "display": "Рано"},
      {"value": "by_trainer", "display": "Отметка тренером"},
      {"value": "unknown", "display": "Неизвестно"}
    ],
    "trust_levels": [
      {"value": "trusted", "display": "Доверенный"},
      {"value": "suspicious", "display": "Подозрительный"},
      {"value": "blocked", "display": "Заблокирован"},
      {"value": "manual_by_trainer", "display": "Ручная отметка"}
    ]
  }
}
```

### Описание полей

**Основная структура ответа:**
- `groups[]` - массив групп участника
- `total_groups` - общее количество групп
- `participant_info` - информация об участнике
- `pagination` - данные пагинации
- `filter_options` - доступные опции для фильтрации
- `message` (опционально) - информационное сообщение
- `details` (опционально) - дополнительные детали

**Participant Info (Информация об участнике):**
- `iin` - ИИН участника
- `full_name` - полное имя участника
- `role` - роль пользователя (обычно "Участник")

**Group (Группа):**
- `id` - уникальный идентификатор группы
- `code` - код группы
- `course_name` - название курса
- `start_date` - дата начала курса
- `end_date` - дата окончания курса
- `sessions_count` - общее количество сессий в группе

**Session (Сессия):**
- `id` - уникальный идентификатор сессии
- `date` - дата сессии
- `is_today` - является ли сессия сегодняшней
- `attendance` - данные о посещаемости (может быть `null`, если участник не посещал)

**Attendance (Посещаемость):**
- `id` - уникальный идентификатор записи посещаемости
- `arrived_at` - время прихода (ISO 8601 формат)
- `arrived_status` - статус прихода (см. filter_options)
- `arrived_status_display` - отображаемое название статуса прихода
- `left_at` - время ухода (может быть `null`)
- `left_status` - статус ухода
- `left_status_display` - отображаемое название статуса ухода
- `trust_level` - уровень доверия (см. filter_options)
- `trust_level_display` - отображаемое название уровня доверия
- `trust_score` - числовой показатель доверия (0-100)
- `marked_entry_by_trainer` - отмечен ли вход тренером вручную
- `marked_exit_by_trainer` - отмечен ли выход тренером вручную

### Коды ошибок

#### **400 Bad Request** - неверные параметры запроса
```json
{
  "error": "Missing required parameter",
  "message": "Параметр participant_iin обязателен",
  "details": "Укажите ИИН участника в параметре participant_iin"
}
```

#### **401 Unauthorized** - отсутствует или неверный токен
```json
{
  "error": "Authentication failed",
  "message": "Недействительный токен"
}
```

#### **403 Forbidden** - недостаточно прав доступа
```json
{
  "error": "Insufficient permissions", 
  "message": "Требуется уровень доступа: read_only"
}
```

#### **404 Not Found** - участник не найден
```json
{
  "error": "Participant not found",
  "message": "Участник с ИИН 123456789012 не найден",
  "details": "Проверьте правильность ИИН или убедитесь, что профиль имеет роль \"Участник\"",
  "groups": [],
  "total_groups": 0,
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 0,
    "total_items": 0
  },
  "filter_options": {...}
}
```

#### **200 OK** - участник найден, но нет групп
```json
{
  "groups": [],
  "total_groups": 0,
  "message": "У участника Иванов Иван Иванович нет активных групп",
  "details": "Возможно, все группы завершены или участник еще не записан ни в одну группу",
  "participant_info": {
    "iin": "123456789012",
    "full_name": "Иванов Иван Иванович",
    "role": "Участник"
  },
  "pagination": {...},
  "filter_options": {...}
}
```

#### **500 Internal Server Error** - внутренняя ошибка сервера

### Примеры использования

**Python (requests):**
```python
import requests

headers = {'Authorization': 'Bearer YOUR_TOKEN'}
params = {'participant_iin': '123456789012', 'page': 1, 'per_page': 5}

response = requests.get(
    'http://localhost:8000/api/groups/my_groups/',
    headers=headers,
    params=params
)

data = response.json()
print(f"Найдено групп: {data['total_groups']}")

for group in data['groups']:
    print(f"Группа: {group['code']} - {group['course_name']}")
    for session in group['sessions']:
        if session['attendance']:
            print(f"  {session['date']}: {session['attendance']['arrived_status_display']}")
        else:
            print(f"  {session['date']}: Не посещал")
```

**JavaScript (fetch):**
```javascript
const headers = {'Authorization': 'Bearer YOUR_TOKEN'};
const params = new URLSearchParams({
    participant_iin: '123456789012',
    page: 1,
    per_page: 5
});

fetch(`http://localhost:8000/api/groups/my_groups/?${params}`, {headers})
    .then(response => response.json())
    .then(data => {
        console.log(`Найдено групп: ${data.total_groups}`);
        
        data.groups.forEach(group => {
            console.log(`Группа: ${group.code} - ${group.course_name}`);
            group.sessions.forEach(session => {
                const status = session.attendance 
                    ? session.attendance.arrived_status_display 
                    : 'Не посещал';
                console.log(`  ${session.date}: ${status}`);
            });
        });
    });
```

## Безопасность

1. **Храните токены в безопасности** - не передавайте их через URL или незащищенные каналы
2. **Используйте HTTPS** в продакшене
3. **Ограничивайте срок действия токенов** - устанавливайте разумные сроки истечения
4. **Мониторьте использование** - следите за активностью токенов
5. **Отзывайте скомпрометированные токены** - немедленно удаляйте подозрительные токены 