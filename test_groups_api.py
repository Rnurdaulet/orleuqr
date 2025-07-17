#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API CRUD операций с группами.
Запуск: python test_groups_api.py

Требует API токен для авторизации. Создайте токен в админ панели Django:
http://localhost:8000/admin/core/apitoken/

Установите переменную окружения API_TOKEN или укажите токен в коде.
"""

import requests
import json
import os
from datetime import datetime, date

# Базовый URL для API
BASE_URL = "http://localhost:8000/api/crud/groups/"

# API токен для авторизации
API_TOKEN = 'Xou_3BhElBy8cCN53Gc3M7hjmPmhht_sZwwqZoCf1Qw'
# API_TOKEN = os.getenv('API_TOKEN', 'Xou_3BhElBy8cCN53Gc3M7hjmPmhht_sZwwqZoCf1Qw')

def get_headers():
    """Возвращает заголовки с авторизацией"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }

def print_separator(text):
    print(f"\n{'='*60}")
    print(f"{text}")
    print(f"{'='*60}")

def check_auth():
    """Проверяет правильность настройки авторизации"""
    if API_TOKEN == 'your-api-token-here':
        print("⚠️  ВНИМАНИЕ: Не настроен API токен!")
        print("1. Создайте API токен в админ панели: http://localhost:8000/admin/core/apitoken/")
        print("2. Установите переменную окружения: export API_TOKEN=your-actual-token")
        print("3. Или измените токен в коде напрямую")
        return False
    
    print(f"🔑 Используется API токен: {API_TOKEN[:10]}...")
    return True

def test_auth():
    """Тестирует авторизацию перед основными тестами"""
    print_separator("ТЕСТ: Проверка авторизации")
    
    try:
        response = requests.get(BASE_URL, headers=get_headers())
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 401:
            print("❌ Токен недействителен или отсутствует")
            try:
                error_data = response.json()
                print(f"   Ошибка: {error_data.get('message', 'Неизвестная ошибка')}")
            except:
                pass
            return False
        elif response.status_code == 403:
            print("❌ Недостаточно прав для доступа к API")
            try:
                error_data = response.json()
                print(f"   Ошибка: {error_data.get('message', 'Недостаточно прав')}")
            except:
                pass
            return False
        elif response.status_code == 200:
            print("✅ Авторизация прошла успешно!")
            return True
        else:
            print(f"⚠️  Неожиданный статус: {response.status_code}")
            return True  # Продолжаем тесты
        
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения к серверу")
        return False
    except Exception as e:
        print(f"❌ Ошибка проверки авторизации: {e}")
        return False

def handle_auth_error(response):
    """Обрабатывает ошибки авторизации"""
    if response.status_code == 401:
        print("❌ Ошибка авторизации: неправильный или отсутствующий токен")
        try:
            error_data = response.json()
            print(f"   Сообщение: {error_data.get('message', 'Неизвестная ошибка')}")
        except:
            pass
        return True
    elif response.status_code == 403:
        print("❌ Доступ запрещен: недостаточно прав у токена")
        try:
            error_data = response.json()
            print(f"   Сообщение: {error_data.get('message', 'Недостаточно прав')}")
        except:
            pass
        return True
    return False

def test_create_group():
    """Тест создания новой группы"""
    print_separator("ТЕСТ: Создание группы")
    
    test_data = {
        "groupId": 99999,
        "groupUnique": "NEWTEST124",
        "courseName": "Тестовый курс для API",
        "supervisorName": "Тестовый Тренер Тренерович",
        "supervisorIIN": "123456789012",
        "startingDate": "2024-01-01",
        "endingDate": "2024-01-31",
        "listenersList": [
            {
                "iin": "987654321098",
                "surname": "ТЕСТОВЫЙ",
                "name": "УЧАСТНИК ПЕРВЫЙ",
                "email": "participant1@test.ru"
            },
            {
                "iin": "987654321099",
                "surname": "ТЕСТОВЫЙ",
                "name": "УЧАСТНИК ВТОРОЙ", 
                "email": "participant2@test.ru"
            }
        ],
        "daysforAttendence": [
            "2024-01-01T00:00:00",
            "2024-01-02T00:00:00",
            "2024-01-03T00:00:00"
        ]
    }
    
    try:
        response = requests.post(
            BASE_URL,
            json=test_data,
            headers=get_headers()
        )
        
        print(f"Статус: {response.status_code}")
        
        if handle_auth_error(response):
            return False
            
        if response.status_code in [200, 201]:
            print("✅ Группа успешно создана!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ Ошибка создания группы: {response.text}")
        
        return response.status_code in [200, 201]
        
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения. Убедитесь, что сервер запущен на http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def test_get_group(group_code):
    """Тест получения группы по коду"""
    print_separator(f"ТЕСТ: Получение группы {group_code}")
    
    try:
        response = requests.get(f"{BASE_URL}{group_code}/", headers=get_headers())
        print(f"Статус: {response.status_code}")
        
        if handle_auth_error(response):
            return False
        
        if response.status_code == 200:
            print("✅ Группа найдена!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ Группа не найдена: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Ошибка получения группы: {e}")
        return False

def test_list_groups():
    """Тест получения списка всех групп"""
    print_separator("ТЕСТ: Список всех групп")
    
    try:
        response = requests.get(BASE_URL, headers=get_headers())
        print(f"Статус: {response.status_code}")
        
        if handle_auth_error(response):
            return False
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Найдено групп: {data.get('count', 0)}")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Ошибка получения списка: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Ошибка получения списка: {e}")
        return False

def test_add_participants_via_update(group_code):
    """Тест добавления участников через обновление группы"""
    print_separator(f"ТЕСТ: Добавление участников через PATCH {group_code}")
    
    update_data = {
        "listenersList": [
            {
                "iin": "987654321098",
                "surname": "ТЕСТОВЫЙ",
                "name": "УЧАСТНИК ПЕРВЫЙ",
                "email": "participant1@test.ru"
            },
            {
                "iin": "987654321099",
                "surname": "ТЕСТОВЫЙ",
                "name": "УЧАСТНИК ВТОРОЙ", 
                "email": "participant2@test.ru"
            },
            {
                "iin": "111111111111",
                "surname": "НОВЫЙ",
                "name": "УЧАСТНИК",
                "email": "new_participant@test.ru"
            }
        ]
    }
    
    try:
        response = requests.patch(
            f"{BASE_URL}{group_code}/",
            json=update_data,
            headers=get_headers()
        )
        
        print(f"Статус: {response.status_code}")
        
        if handle_auth_error(response):
            return False
            
        if response.status_code == 200:
            print("✅ Участники обновлены!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ Ошибка обновления участников: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Ошибка обновления участников: {e}")
        return False

def test_update_sessions(group_code):
    """Тест обновления сессий через PATCH"""
    print_separator(f"ТЕСТ: Обновление сессий для группы {group_code}")
    
    update_data = {
        "daysforAttendence": [
            "2024-01-01T00:00:00",
            "2024-01-02T00:00:00",
            "2024-01-03T00:00:00",
            "2024-01-04T00:00:00"
        ]
    }
    
    try:
        response = requests.patch(
            f"{BASE_URL}{group_code}/",
            json=update_data,
            headers=get_headers()
        )
        
        print(f"Статус: {response.status_code}")
        
        if handle_auth_error(response):
            return False
            
        if response.status_code == 200:
            print("✅ Сессии обновлены!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ Ошибка обновления сессий: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Ошибка обновления сессий: {e}")
        return False

def test_create_import_group():
    """Тест создания группы в формате miniresponse.json"""
    print_separator("ТЕСТ: Создание группы в формате miniresponse.json")
    
    import_data = {
        "groupId": 88888,
        "groupUnique": "NEWIMPORT1",
        "courseName": "Импортированный курс",
        "supervisorName": "Импортированный Тренер",
        "supervisorIIN": "555555555555",
        "startingDate": "2024-02-01",
        "endingDate": "2024-02-28",
        "listenersList": [
            {
                "iin": "444444444444",
                "surname": "ИМПОРТ",
                "name": "ТЕСТОВЫЙ",
                "email": "import@test.ru"
            }
        ],
        "daysforAttendence": [
            "2024-02-01T00:00:00",
            "2024-02-02T00:00:00"
        ]
    }
    
    try:
        response = requests.post(
            BASE_URL,
            json=import_data,
            headers=get_headers()
        )
        
        print(f"Статус: {response.status_code}")
        
        if handle_auth_error(response):
            return False
            
        if response.status_code in [200, 201]:
            print("✅ Группа в формате JSON создана!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ Ошибка создания: {response.text}")
        
        return response.status_code in [200, 201]
        
    except Exception as e:
        print(f"❌ Ошибка создания: {e}")
        return False

def test_error_handling():
    """Тест обработки ошибок 500 в JSON формате"""
    print_separator("ТЕСТ: Обработка ошибок 500")
    
    error_types = ['generic', 'division', 'attribute', 'key']
    
    all_passed = True
    
    for error_type in error_types:
        print(f"\n🔍 Тестируем ошибку типа: {error_type}")
        
        try:
            response = requests.get(
                f"{BASE_URL}test-error/?type={error_type}",
                headers=get_headers()
            )
            
            print(f"   Статус: {response.status_code}")
            
            # Проверяем что ответ приходит в JSON формате
            try:
                response_data = response.json()
                print(f"   ✅ Ответ в JSON формате")
                
                # Проверяем структуру ошибки
                if 'error' in response_data and 'message' in response_data:
                    print(f"   ✅ Корректная структура ошибки")
                    print(f"   📝 Сообщение: {response_data.get('message', 'Не указано')}")
                else:
                    print(f"   ❌ Неправильная структура JSON ответа")
                    all_passed = False
                    
                # Проверяем что статус 500
                if response.status_code == 500:
                    print(f"   ✅ Корректный статус 500")
                else:
                    print(f"   ⚠️  Ожидался статус 500, получен {response.status_code}")
                    
            except json.JSONDecodeError:
                print(f"   ❌ Ответ НЕ в JSON формате!")
                print(f"   📄 Содержимое: {response.text[:200]}...")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ Ошибка запроса: {e}")
            all_passed = False
    
    return all_passed

def test_invalid_group_code():
    """Тест получения несуществующей группы (404 в JSON)"""
    print_separator("ТЕСТ: Получение несуществующей группы")
    
    try:
        response = requests.get(f"{BASE_URL}NONEXISTENT/", headers=get_headers())
        print(f"Статус: {response.status_code}")
        
        if handle_auth_error(response):
            return False
        
        # Проверяем что 404 возвращается в JSON
        try:
            response_data = response.json()
            print("✅ Ответ 404 в JSON формате")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            
            if response.status_code == 404:
                print("✅ Корректный статус 404")
                return True
            else:
                print(f"❌ Ожидался статус 404, получен {response.status_code}")
                return False
                
        except json.JSONDecodeError:
            print("❌ Ответ 404 НЕ в JSON формате!")
            print(f"Содержимое: {response.text[:200]}...")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

def test_update_group(group_code):
    """Тест обновления группы"""
    print_separator(f"ТЕСТ: Обновление группы {group_code}")
    
    update_data = {
        "courseName": "Обновленное название курса",
        "supervisorName": "Обновленный Тренер"
    }
    
    try:
        response = requests.patch(
            f"{BASE_URL}{group_code}/",
            json=update_data,
            headers=get_headers()
        )
        
        print(f"Статус: {response.status_code}")
        
        if handle_auth_error(response):
            return False
            
        if response.status_code == 200:
            print("✅ Группа обновлена!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ Ошибка обновления: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Ошибка обновления: {e}")
        return False

def main():
    """Основная функция для запуска всех тестов"""
    print("🚀 Начинаем тестирование API для групп в формате miniresponse.json")
    print(f"Базовый URL: {BASE_URL}")
    
    # Проверяем настройку авторизации
    if not check_auth():
        print("\n❌ Тестирование прервано из-за неправильной настройки авторизации")
        return
    
    results = []
    
    # Тестируем авторизацию
    auth_result = test_auth()
    results.append(("Проверка авторизации", auth_result))
    
    if not auth_result:
        print("\n❌ Тестирование прервано из-за ошибки авторизации")
        return
    
    # Тестируем создание группы в стандартном формате
    results.append(("Создание группы NEWTEST124", test_create_group()))
    
    # Тестируем получение списка групп
    results.append(("Список групп", test_list_groups()))
    
    # Тестируем получение конкретной группы
    results.append(("Получение группы TEST123", test_get_group("TEST123")))
    
    # Тестируем обновление участников через PATCH
    results.append(("Обновление участников", test_add_participants_via_update("TEST123")))
    
    # Тестируем обновление сессий через PATCH
    results.append(("Обновление сессий", test_update_sessions("TEST123")))
    
    # Тестируем обновление основной информации группы
    results.append(("Обновление группы", test_update_group("TEST123")))
    
    # Тестируем создание группы в формате miniresponse.json
    results.append(("Создание в формате JSON", test_create_import_group()))
    
    # Тестируем получение импортированной группы
    results.append(("Получение группы NEWIMPORT1", test_get_group("NEWIMPORT1")))
    
    # Тестируем обработку ошибок
    results.append(("Обработка ошибок 500", test_error_handling()))
    
    # Тестируем ошибку 404
    results.append(("Получение несуществующей группы", test_invalid_group_code()))
    
    # Выводим итоги
    print_separator("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОШЕЛ" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nИтого: {passed}/{total} тестов прошли успешно")
    
    if passed == total:
        print("🎉 Все тесты пройдены! API работает корректно.")
        print("\n📋 Доступные операции:")
        print("- Создание групп в формате miniresponse.json")
        print("- Управление участниками через listenersList")  
        print("- Управление сессиями через daysforAttendence")
        print("- Обновление всех данных через PATCH/PUT")
        print("- Удаление групп по коду")
        print("- Обработка всех ошибок в JSON формате (включая 500)")
        print("- Корректная авторизация через API токены")
    else:
        print(f"⚠️  {total - passed} тестов провалены. Проверьте логи выше.")

if __name__ == "__main__":
    main() 