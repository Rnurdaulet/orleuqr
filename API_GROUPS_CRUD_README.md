# API CRUD для управления группами в формате miniresponse.json

## Обзор

Реализован REST API для полного управления группами через уникальный код группы (поле `code`). 
**API работает ТОЧНО в том же формате, что и файл miniresponse.json** - все поля, структура данных и форматы соответствуют оригинальному JSON файлу.

Все операции (группы, участники, сессии) управляются через единый CRUD API.

## Базовый URL

```
http://your-domain.com/api/crud/groups/
```

## Аутентификация

API использует токен-аутентификацию через заголовок `Authorization`. 

### Получение токена

1. Создайте API токен в админ панели Django: `http://your-domain.com/admin/core/apitoken/`
2. Выберите уровень доступа:
   - `read_only` - только чтение
   - `read_write` - чтение и запись  
   - `admin` - полный доступ

### Использование токена

Все запросы должны содержать заголовок:
```
Authorization: Bearer your-api-token-here
```

### Пример запроса

```bash
curl -X GET http://localhost:8000/api/crud/groups/ \
  -H "Authorization: Bearer your-api-token-here" \
  -H "Content-Type: application/json"
```

## Основные эндпоинты

### 1. Список всех групп
```http
GET /api/crud/groups/
```

**Ответ:**
```json
{
  "count": 2,
  "results": [
    {
      "groupId": 14462,
      "groupUnique": "26EB9T",
      "courseName": "Бастауыш сынып оқушыларының зерттеушілік",
      "supervisorName": "Ильясова Гульзира",
      "startingDate": "2025-07-11",
      "endingDate": "2025-07-18",
      "participantsCount": 32,
      "trainersCount": 1
    }
  ]
}
```

### 2. Получить группу по коду
```http
GET /api/crud/groups/{code}/
```

**Пример запроса:**
```http
GET /api/crud/groups/26EB9T/
```

**Ответ:**
```json
{
  "groupId": 14462,
  "groupUnique": "26EB9T",
  "courseName": "Бастауыш сынып оқушыларының зерттеушілік",
  "supervisorName": "Ильясова Гульзира",
  "supervisorIIN": "831212401667",
  "startingDate": "2025-07-11",
  "endingDate": "2025-07-18",
  "use_time_limits": false,
  "listenersList": [
    {
      "iin": "841105401171",
      "full_name": "АЛИМКУЛОВА КУНДУЗАЙ",
      "email": "alimkulova_k@mail.ru",
      "role": "participant"
    }
  ],
  "trainersList": [
    {
      "iin": "831212401667",
      "full_name": "Ильясова Гульзира",
      "email": "",
      "role": "trainer"
    }
  ],
  "daysforAttendence": [
    "2025-07-11",
    "2025-07-12"
  ],
  "sessions": [
    {
      "date": "2025-07-11",
      "entry_start": "09:00:00",
      "entry_end": "10:00:00",
      "exit_start": "17:00:00",
      "exit_end": "18:00:00",
      "qr_token_entry": "550e8400-e29b-41d4-a716-446655440000",
      "qr_token_exit": "550e8400-e29b-41d4-a716-446655440001"
    }
  ]
}
```

### 3. Создать новую группу
```http
POST /api/crud/groups/
```

**Тело запроса (точный формат miniresponse.json):**
```json
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
    },
    {
      "iin": "850822401832",
      "surname": "СУЙЕРКУЛОВА",
      "name": "МАРЖАН",
      "email": "suierkulovamarjan@gmail.com"
    }
  ],
  "daysforAttendence": [
    "2025-07-11T00:00:00",
    "2025-07-12T00:00:00",
    "2025-07-13T00:00:00"
  ]
}
```

### 4. Обновить группу
```http
PUT /api/crud/groups/{code}/     # Полное обновление
PATCH /api/crud/groups/{code}/   # Частичное обновление
```

**Пример частичного обновления:**
```json
{
  
  "supervisorName": "Новый тренер"
}
```

### 5. Удалить группу
```http
DELETE /api/crud/groups/{code}/
```

## Управление участниками и сессиями

**Все управление участниками и сессиями происходит через основные CRUD операции**

### Обновить участников группы
```http
PATCH /api/crud/groups/{code}/
```

**Тело запроса:**
```json
{
  "listenersList": [
    {
      "iin": "841105401171",
      "surname": "АЛИМКУЛОВА",
      "name": "КУНДУЗАЙ",
      "email": "alimkulova_k@mail.ru"
    },
    {
      "iin": "111111111111",
      "surname": "НОВЫЙ",
      "name": "УЧАСТНИК",
      "email": "new@example.com"
    }
  ]
}
```

### Обновить сессии группы
```http
PATCH /api/crud/groups/{code}/
```

**Тело запроса:**
```json
{
  "daysforAttendence": [
    "2024-01-01T00:00:00",
    "2024-01-02T00:00:00",
    "2024-01-03T00:00:00",
    "2024-01-04T00:00:00"
  ]
}
```

### Одновременное обновление участников и сессий
```http
PATCH /api/crud/groups/{code}/
```

**Тело запроса:**
```json
{
  "courseName": "Обновленное название курса",
  "listenersList": [
    {
      "iin": "841105401171",
      "surname": "ОБНОВЛЕННЫЙ",
      "name": "УЧАСТНИК",
      "email": "updated@example.com"
    }
  ],
  "daysforAttendence": [
    "2024-01-01T00:00:00",
    "2024-01-02T00:00:00"
  ]
}
```

## Импорт из miniresponse.json

**Импорт происходит через обычный POST запрос для создания группы** - просто отправьте данные из miniresponse.json как есть:

```http
POST /api/crud/groups/
```

Можете взять любой объект из массива в miniresponse.json и отправить его напрямую!

## Коды ошибок

Все ошибки возвращаются в JSON формате:

- `200` - Успешный запрос
- `201` - Ресурс создан
- `204` - Ресурс удален
- `400` - Неверные данные запроса
- `401` - Не авторизован
- `404` - Группа не найдена
- `500` - Внутренняя ошибка сервера

### Формат ошибок

Все ошибки возвращаются в едином JSON формате:

```json
{
  "error": true,
  "status_code": 404,
  "message": "Ресурс не найден",
  "details": "Группа с кодом 'ABC123' не существует",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Тестирование ошибок

Для тестирования обработки ошибок 500 используйте специальный endpoint:

```bash
# Тест общей ошибки
curl -X GET "http://localhost:8000/api/crud/groups/test-error/" \
  -H "Authorization: Bearer your-token"

# Тест ошибки деления на ноль
curl -X GET "http://localhost:8000/api/crud/groups/test-error/?type=division" \
  -H "Authorization: Bearer your-token"

# Тест ошибки атрибута
curl -X GET "http://localhost:8000/api/crud/groups/test-error/?type=attribute" \
  -H "Authorization: Bearer your-token"
```

## Примеры использования

### Создание группы с последующим добавлением сессий

1. **Создать группу:**
```bash
curl -X POST http://localhost:8000/api/crud/groups/ \
  -H "Authorization: Bearer your-api-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "groupId": 12345,
    "groupUnique": "DEMO123",
    "courseName": "Демо курс",
    "supervisorName": "Демо Тренер",
    "supervisorIIN": "123456789012",
    "startingDate": "2024-01-01T00:00:00",
    "endingDate": "2024-01-31T00:00:00",
    "listenersList": [
      {
        "iin": "987654321098",
        "surname": "ДЕМО",
        "name": "УЧАСТНИК",
        "email": "demo@example.com"
      }
    ],
    "daysforAttendence": [
      "2024-01-01T00:00:00",
      "2024-01-02T00:00:00"
    ]
  }'
```

2. **Обновить участников:**
```bash
curl -X PATCH http://localhost:8000/api/crud/groups/DEMO123/ \
  -H "Authorization: Bearer your-api-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "listenersList": [
      {
        "iin": "987654321098",
        "surname": "ДЕМО",
        "name": "УЧАСТНИК",
        "email": "demo@example.com"
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

3. **Обновить сессии:**
```bash
curl -X PATCH http://localhost:8000/api/crud/groups/DEMO123/ \
  -H "Authorization: Bearer your-api-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "daysforAttendence": [
      "2024-01-01T00:00:00",
      "2024-01-02T00:00:00",
      "2024-01-03T00:00:00"
    ]
  }'
```

## Тестирование

Для тестирования API используйте приложенный скрипт `test_groups_api.py`:

### Подготовка

1. Создайте API токен в админ панели: `http://localhost:8000/admin/core/apitoken/`
2. Установите переменную окружения с токеном:
   ```bash
   export API_TOKEN=your-actual-api-token
   ```
   
   Или измените токен в файле `test_groups_api.py` напрямую:
   ```python
   API_TOKEN = "your-actual-api-token"
   ```

### Запуск тестов

```bash
# Убедитесь, что сервер запущен
python manage.py runserver

# В другом терминале запустите тесты
python test_groups_api.py
```

### Что тестируется

- ✅ Проверка авторизации и токена
- ✅ Создание групп в формате miniresponse.json
- ✅ Получение списка и отдельных групп
- ✅ Обновление участников через listenersList
- ✅ Обновление сессий через daysforAttendence
- ✅ Частичное и полное обновление групп

## Структура файлов

- `apps/groups/api.py` - ViewSet для API
- `apps/groups/serializers.py` - Сериализаторы
- `apps/groups/api_urls.py` - URL роутинг для API
- `test_groups_api.py` - Тестовый скрипт

## Особенности реализации

1. **Формат miniresponse.json:** API принимает и возвращает данные ТОЧНО в том же формате, что и файл miniresponse.json
2. **Lookup по коду:** Все операции выполняются через поле `code` вместо `id`
3. **Единый CRUD:** Управление группами, участниками и сессиями через один API
4. **Автоматическое создание профилей:** При добавлении участников/тренеров автоматически создаются профили PersonProfile
5. **Формат участников:** `surname` + `name` вместо `full_name`
6. **Формат дат:** `"2025-07-11T00:00:00"` для всех дат
7. **Автоматические сессии:** Сессии создаются из `daysforAttendence` с настройками по умолчанию
8. **Тренер из руководителя:** Тренер автоматически создается из `supervisorName`/`supervisorIIN`

## Ключевые отличия от стандартного API

- **Формат участников:** `listenersList` с полями `surname`, `name`, а не `full_name`
- **Формат сессий:** `daysforAttendence` с датами в ISO формате
- **Нет отдельных эндпоинтов:** Все управляется через основные CRUD операции
- **Точное соответствие:** 100% совместимость с форматом miniresponse.json

## Совместимость

API совместим с существующим функционалом проекта и не нарушает работу существующих эндпоинтов в `/api/groups/`.
Новый API доступен по адресу `/api/crud/groups/` и работает параллельно с существующим. 