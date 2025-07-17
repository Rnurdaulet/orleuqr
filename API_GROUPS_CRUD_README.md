# API для управления группами - Руководство для разработчиков

## 📋 Обзор

Этот API предоставляет полное CRUD управление группами, участниками и сессиями через единый интерфейс. API полностью совместим с форматом `miniresponse.json` и предназначен для интеграции с внешними сервисами.

### 🎯 Ключевые особенности

- **Единый CRUD**: Все операции (группы, участники, сессии) через один API
- **Формат miniresponse.json**: 100% совместимость с существующими данными
- **Lookup по коду**: Все операции через уникальный код группы
- **JSON ошибки**: Все ошибки (включая 500) возвращаются в JSON формате [[memory:3512263]]
- **Автоматическое создание**: Участники и тренеры создаются автоматически
- **Гибкие обновления**: Частичные и полные обновления

## 🔗 Базовая информация

### Endpoint
```
POST,GET,PUT,PATCH,DELETE /api/crud/groups/
GET,PUT,PATCH,DELETE      /api/crud/groups/{code}/
```

### Аутентификация [[memory:3511100]]
Все запросы требуют API токен в заголовке:
```http
Authorization: Bearer your-api-token-here
```

### Формат данных
Все даты в формате ISO: `"2025-07-11T00:00:00"`  
Все поля точно как в `miniresponse.json`

## 🚀 Быстрый старт

### 1. Получение API токена

Создайте токен в админ панели:
```
http://your-domain.com/admin/core/apitoken/
```

Выберите уровень доступа:
- `read_only` - только чтение
- `read_write` - чтение и запись  
- `admin` - полный доступ

### 2. Базовый запрос

```bash
curl -X GET http://localhost:8000/api/crud/groups/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### 3. Проверка подключения

```bash
# Получить список групп
GET /api/crud/groups/

# Ответ при успехе (200)
{
  "count": 2,
  "results": [
    {
      "groupId": 14462,
      "groupUnique": "26EB9T",
      "courseName": "Тестовый курс",
      "supervisorName": "Иванов Иван",
      "startingDate": "2025-07-11",
      "endingDate": "2025-07-18",
      "participantsCount": 32,
      "trainersCount": 1
    }
  ]
}
```

## 📖 Подробная документация API

### 1. Получение списка групп

```http
GET /api/crud/groups/
```

**Ответ:**
```json
{
  "count": 10,
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

### 2. Получение группы по коду

```http
GET /api/crud/groups/{code}/
```

**Пример:**
```bash
curl -X GET http://localhost:8000/api/crud/groups/26EB9T/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Ответ:**
```json
{
  "groupId": 14462,
  "groupUnique": "26EB9T",
  "courseName": "Бастауыш сынып оқушыларының зерттеушілік",
  "supervisorName": "Ильясова Гульзира",
  "supervisorIIN": "831212401667",
  "startingDate": "2025-07-11T00:00:00",
  "endingDate": "2025-07-18T00:00:00",
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
    "2025-07-11T00:00:00",
    "2025-07-12T00:00:00"
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

### 3. Создание новой группы

```http
POST /api/crud/groups/
```

**Тело запроса (точный формат miniresponse.json):**
```json
{
  "groupId": 14462,
  "groupUnique": "TEST123",
  "courseName": "Новый тестовый курс",
  "supervisorName": "Иванов Иван Иванович",
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

**Curl пример:**
```bash
curl -X POST http://localhost:8000/api/crud/groups/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "groupId": 99999,
    "groupUnique": "NEWTEST124",
    "courseName": "Тестовый курс для API",
    "supervisorName": "Тестовый Тренер Тренерович",
    "supervisorIIN": "123456789012",
    "startingDate": "2024-01-01T00:00:00",
    "endingDate": "2024-01-31T00:00:00",
    "listenersList": [
      {
        "iin": "987654321098",
        "surname": "ТЕСТОВЫЙ",
        "name": "УЧАСТНИК",
        "email": "participant@test.ru"
      }
    ],
    "daysforAttendence": [
      "2024-01-01T00:00:00",
      "2024-01-02T00:00:00"
    ]
  }'
```

### 4. Обновление группы

#### Полное обновление (PUT)
```http
PUT /api/crud/groups/{code}/
```

#### Частичное обновление (PATCH)
```http
PATCH /api/crud/groups/{code}/
```

**Примеры частичного обновления:**

##### Обновить только название курса:
```json
{
  "courseName": "Обновленное название курса"
}
```

##### Обновить участников:
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

##### Обновить сессии:
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

##### Комбинированное обновление:
```json
{
  "courseName": "Обновленное название",
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

### 5. Удаление группы

```http
DELETE /api/crud/groups/{code}/
```

**Пример:**
```bash
curl -X DELETE http://localhost:8000/api/crud/groups/TEST123/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Ответ:**
```json
{
  "message": "Группа успешно удалена"
}
```

## 🔧 Практические сценарии

### Сценарий 1: Импорт данных из miniresponse.json

```python
import requests
import json

# Читаем данные из файла
with open('miniresponse.json', 'r', encoding='utf-8') as f:
    groups_data = json.load(f)

headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}

# Импортируем каждую группу
for group in groups_data:
    response = requests.post(
        'http://localhost:8000/api/crud/groups/',
        json=group,
        headers=headers
    )
    
    if response.status_code == 201:
        print(f"✅ Группа {group['groupUnique']} создана")
    else:
        print(f"❌ Ошибка: {response.text}")
```

### Сценарий 2: Массовое обновление участников

```python
# Получаем все группы
response = requests.get(
    'http://localhost:8000/api/crud/groups/',
    headers=headers
)

groups = response.json()['results']

# Добавляем нового участника в каждую группу
new_participant = {
    "iin": "999999999999",
    "surname": "НОВЫЙ",
    "name": "УЧАСТНИК",
    "email": "new@example.com"
}

for group in groups:
    group_code = group['groupUnique']
    
    # Получаем текущих участников
    group_response = requests.get(
        f'http://localhost:8000/api/crud/groups/{group_code}/',
        headers=headers
    )
    
    current_group = group_response.json()
    current_participants = current_group.get('listenersList', [])
    
    # Добавляем нового участника
    current_participants.append(new_participant)
    
    # Обновляем группу
    update_response = requests.patch(
        f'http://localhost:8000/api/crud/groups/{group_code}/',
        json={'listenersList': current_participants},
        headers=headers
    )
    
    if update_response.status_code == 200:
        print(f"✅ Участник добавлен в группу {group_code}")
```

### Сценарий 3: Создание групп с расписанием

```python
def create_group_with_schedule(course_name, supervisor_name, supervisor_iin, 
                             start_date, duration_days, participants):
    """
    Создает группу с автоматически сгенерированным расписанием
    """
    from datetime import datetime, timedelta
    
    # Генерируем уникальный код
    import random, string
    group_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Генерируем даты сессий
    start = datetime.strptime(start_date, '%Y-%m-%d')
    sessions = []
    for i in range(duration_days):
        session_date = start + timedelta(days=i)
        sessions.append(session_date.strftime('%Y-%m-%dT00:00:00'))
    
    group_data = {
        "groupId": random.randint(10000, 99999),
        "groupUnique": group_code,
        "courseName": course_name,
        "supervisorName": supervisor_name,
        "supervisorIIN": supervisor_iin,
        "startingDate": f"{start_date}T00:00:00",
        "endingDate": f"{(start + timedelta(days=duration_days-1)).strftime('%Y-%m-%d')}T00:00:00",
        "listenersList": participants,
        "daysforAttendence": sessions
    }
    
    response = requests.post(
        'http://localhost:8000/api/crud/groups/',
        json=group_data,
        headers=headers
    )
    
    return response

# Использование
participants = [
    {
        "iin": "123456789012",
        "surname": "ИВАНОВ",
        "name": "ИВАН",
        "email": "ivan@example.com"
    }
]

result = create_group_with_schedule(
    course_name="Python для начинающих",
    supervisor_name="Петров Петр Петрович",
    supervisor_iin="987654321098",
    start_date="2024-02-01",
    duration_days=5,
    participants=participants
)
```

## ⚠️ Обработка ошибок

Все ошибки возвращаются в едином JSON формате:

### Коды состояния
- `200` - Успешный запрос
- `201` - Ресурс создан
- `204` - Ресурс удален
- `400` - Неверные данные запроса
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Группа не найдена
- `500` - Внутренняя ошибка сервера

### Формат ошибок
```json
{
  "error": true,
  "status_code": 404,
  "message": "Ресурс не найден",
  "details": "Группа с кодом 'ABC123' не существует",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Примеры обработки ошибок

```python
def safe_api_request(method, url, **kwargs):
    """Безопасный запрос к API с обработкой ошибок"""
    try:
        response = requests.request(method, url, **kwargs)
        
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        elif response.status_code == 201:
            return {'success': True, 'data': response.json(), 'created': True}
        elif response.status_code == 204:
            return {'success': True, 'deleted': True}
        else:
            # Все ошибки приходят в JSON формате
            error_data = response.json()
            return {
                'success': False,
                'error': error_data,
                'status_code': response.status_code
            }
            
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': {'message': 'Не удается подключиться к серверу'},
            'status_code': 0
        }
    except json.JSONDecodeError:
        return {
            'success': False,
            'error': {'message': 'Некорректный ответ сервера'},
            'status_code': response.status_code
        }

# Использование
result = safe_api_request(
    'GET',
    'http://localhost:8000/api/crud/groups/TEST123/',
    headers=headers
)

if result['success']:
    print("Группа найдена:", result['data']['courseName'])
else:
    print("Ошибка:", result['error']['message'])
```

### Тестирование обработки ошибок

Для тестирования обработки ошибок 500 используйте:

```bash
# Тест общей ошибки
curl -X GET "http://localhost:8000/api/crud/groups/test-error/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Тест ошибки деления на ноль  
curl -X GET "http://localhost:8000/api/crud/groups/test-error/?type=division" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Тест ошибки атрибута
curl -X GET "http://localhost:8000/api/crud/groups/test-error/?type=attribute" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🧪 Тестирование API

### Подготовка к тестированию

1. Создайте API токен в админ панели
2. Убедитесь, что сервер запущен на `http://localhost:8000`
3. Установите переменную окружения:

```bash
export API_TOKEN=your-actual-api-token
```

### Автоматическое тестирование

Используйте приложенный скрипт `test_groups_api.py`:

```bash
python test_groups_api.py
```

Скрипт проверит:
- ✅ Авторизацию и токен
- ✅ Создание групп
- ✅ Получение списка и отдельных групп  
- ✅ Обновление участников и сессий
- ✅ Обработку ошибок в JSON формате

### Ручное тестирование

```bash
# 1. Проверка подключения
curl -X GET http://localhost:8000/api/crud/groups/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. Создание тестовой группы
curl -X POST http://localhost:8000/api/crud/groups/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "groupId": 99999,
    "groupUnique": "TEST001",
    "courseName": "Тестовый курс",
    "supervisorName": "Тестовый Тренер",
    "supervisorIIN": "123456789012",
    "startingDate": "2024-01-01T00:00:00",
    "endingDate": "2024-01-31T00:00:00",
    "listenersList": [],
    "daysforAttendence": ["2024-01-01T00:00:00"]
  }'

# 3. Получение созданной группы
curl -X GET http://localhost:8000/api/crud/groups/TEST001/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Удаление тестовой группы
curl -X DELETE http://localhost:8000/api/crud/groups/TEST001/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📝 Важные особенности

### Формат данных
1. **Участники**: Используется `surname` + `name` вместо `full_name`
2. **Даты**: Все даты в формате `"2025-07-11T00:00:00"`
3. **Lookup**: Все операции по полю `code` (не `id`)
4. **Автосоздание**: Участники и тренеры создаются автоматически

### Автоматические процессы
1. **Тренер**: Создается из `supervisorName`/`supervisorIIN`
2. **Профили**: Участники получают профили `PersonProfile`  
3. **Сессии**: Создаются из `daysforAttendence` с настройками по умолчанию
4. **QR-коды**: Генерируются автоматически для каждой сессии

### Производительность
1. **Prefetch**: Связанные объекты предзагружаются
2. **Pagination**: Поддерживается для больших списков
3. **Validation**: Все данные валидируются перед сохранением

## 🔗 Интеграция с вашим сервисом

### Базовый клиент Python

```python
class OrleqrGroupsClient:
    def __init__(self, base_url, api_token):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
    
    def get_groups(self):
        """Получить список всех групп"""
        response = requests.get(f'{self.base_url}/api/crud/groups/', headers=self.headers)
        return response.json()
    
    def get_group(self, code):
        """Получить группу по коду"""
        response = requests.get(f'{self.base_url}/api/crud/groups/{code}/', headers=self.headers)
        return response.json()
    
    def create_group(self, group_data):
        """Создать новую группу"""
        response = requests.post(f'{self.base_url}/api/crud/groups/', json=group_data, headers=self.headers)
        return response.json()
    
    def update_group(self, code, group_data, partial=True):
        """Обновить группу"""
        method = 'PATCH' if partial else 'PUT'
        response = requests.request(method, f'{self.base_url}/api/crud/groups/{code}/', json=group_data, headers=self.headers)
        return response.json()
    
    def delete_group(self, code):
        """Удалить группу"""
        response = requests.delete(f'{self.base_url}/api/crud/groups/{code}/', headers=self.headers)
        return response.status_code == 204

# Использование
client = OrleqrGroupsClient('http://localhost:8000', 'YOUR_TOKEN')
groups = client.get_groups()
```

### JavaScript/Node.js клиент

```javascript
class OrleqrGroupsClient {
    constructor(baseUrl, apiToken) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.headers = {
            'Authorization': `Bearer ${apiToken}`,
            'Content-Type': 'application/json'
        };
    }
    
    async getGroups() {
        const response = await fetch(`${this.baseUrl}/api/crud/groups/`, {
            headers: this.headers
        });
        return await response.json();
    }
    
    async getGroup(code) {
        const response = await fetch(`${this.baseUrl}/api/crud/groups/${code}/`, {
            headers: this.headers
        });
        return await response.json();
    }
    
    async createGroup(groupData) {
        const response = await fetch(`${this.baseUrl}/api/crud/groups/`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(groupData)
        });
        return await response.json();
    }
    
    async updateGroup(code, groupData, partial = true) {
        const method = partial ? 'PATCH' : 'PUT';
        const response = await fetch(`${this.baseUrl}/api/crud/groups/${code}/`, {
            method: method,
            headers: this.headers,
            body: JSON.stringify(groupData)
        });
        return await response.json();
    }
    
    async deleteGroup(code) {
        const response = await fetch(`${this.baseUrl}/api/crud/groups/${code}/`, {
            method: 'DELETE',
            headers: this.headers
        });
        return response.status === 204;
    }
}

// Использование
const client = new OrleqrGroupsClient('http://localhost:8000', 'YOUR_TOKEN');
const groups = await client.getGroups();
```

## 📞 Поддержка

При возникновении проблем:

1. **Проверьте токен**: Убедитесь, что токен действителен и имеет нужные права
2. **Проверьте формат**: Все данные должны точно соответствовать `miniresponse.json`
3. **Логи**: Проверьте логи сервера для детальной информации об ошибках
4. **Тестирование**: Используйте `test_groups_api.py` для диагностики

### Файлы проекта
- `apps/groups/api.py` - ViewSet для API
- `apps/groups/serializers.py` - Сериализаторы данных
- `apps/groups/api_urls.py` - URL маршруты
- `test_groups_api.py` - Скрипт тестирования

## 🆚 Совместимость

API работает параллельно с существующими эндпоинтами в `/api/groups/` и не нарушает существующий функционал. Новый API доступен по адресу `/api/crud/groups/` и полностью автономен. 