#!/usr/bin/env python3
"""
Тестовый скрипт для демонстрации работы API групп и посещаемости
"""

import requests
import json
import sys
from datetime import datetime


class APIClient:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def test_health_check(self):
        """Проверка работоспособности API"""
        print("🔍 Проверка работоспособности API...")
        
        try:
            response = requests.get(f"{self.base_url}/api/health/", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API работает корректно")
                print(f"   Сервис: {data.get('authenticated_service')}")
                print(f"   Права: {data.get('permissions')}")
                print(f"   Время: {data.get('timestamp')}")
                return True
            else:
                print(f"❌ Ошибка: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка соединения: {e}")
            return False
    
    def test_my_groups(self, participant_iin, page=1, per_page=5):
        """Тест получения групп участника"""
        print(f"\n👥 Получение групп для участника {participant_iin}...")
        
        try:
            params = {
                'participant_iin': participant_iin,
                'page': page,
                'per_page': per_page
            }
            
            response = requests.get(
                f"{self.base_url}/api/groups/my_groups/",
                headers=self.headers,
                params=params
            )
            
            data = response.json()
            
            if response.status_code == 200:
                print(f"✅ Найдено групп: {data['total_groups']}")
                
                # Информация об участнике
                if 'participant_info' in data:
                    participant = data['participant_info']
                    print(f"   Участник: {participant['full_name']} ({participant['role']})")
                
                # Пагинация
                print(f"   Страница: {data['pagination']['page']} из {data['pagination']['total_pages']}")
                
                # Если есть дополнительное сообщение (например, нет групп)
                if 'message' in data:
                    print(f"   ℹ️ {data['message']}")
                    if 'details' in data:
                        print(f"   📝 {data['details']}")
                
                # Показываем группы
                for group in data['groups']:
                    print(f"\n📚 Группа: {group['code']} - {group['course_name']}")
                    print(f"   Период: {group['start_date']} — {group['end_date']}")
                    print(f"   Сессий: {group['sessions_count']}")
                    
                    print("   📅 Посещаемость:")
                    for session in group['sessions'][:3]:  # Показываем только первые 3 сессии
                        status_icon = "🟢" if session['is_today'] else "📅"
                        
                        if session['attendance']:
                            att = session['attendance']
                            arrived = att['arrived_at'][:16] if att['arrived_at'] else 'Не пришел'
                            left = att['left_at'][:16] if att['left_at'] else 'Не ушел'
                            trust_icon = {"trusted": "🟢", "suspicious": "🟡", "blocked": "🔴"}.get(att['trust_level'], "❓")
                            
                            print(f"      {status_icon} {session['date']}: {att['arrived_status_display']} ({arrived} — {left}) {trust_icon}")
                        else:
                            print(f"      {status_icon} {session['date']}: Не посещал")
                
                # Показываем доступные фильтры только если есть группы
                if data['total_groups'] > 0:
                    print("\n🔍 Доступные фильтры:")
                    print("   Статусы прихода:", [s['display'] for s in data['filter_options']['arrival_statuses']])
                    print("   Уровни доверия:", [t['display'] for t in data['filter_options']['trust_levels']])
                
                return data
                
            elif response.status_code == 404:
                print(f"❌ {data.get('message', 'Участник не найден')}")
                if 'details' in data:
                    print(f"   📝 {data['details']}")
                return None
                
            elif response.status_code == 400:
                print(f"❌ {data.get('message', 'Неверные параметры')}")
                if 'details' in data:
                    print(f"   📝 {data['details']}")
                return None
            else:
                print(f"❌ Ошибка: {response.status_code}")
                print(f"   {data.get('message', response.text)}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка соединения: {e}")
            return None
    
    def test_missing_parameter(self):
        """Тест отсутствия обязательного параметра"""
        print(f"\n🚫 Тест отсутствия параметра participant_iin...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/groups/my_groups/",
                headers=self.headers
            )
            
            data = response.json()
            print(f"   Статус: {response.status_code}")
            print(f"   Сообщение: {data.get('message')}")
            if 'details' in data:
                print(f"   Детали: {data['details']}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка соединения: {e}")
    
    def test_nonexistent_participant(self, fake_iin="999999999999"):
        """Тест несуществующего участника"""
        print(f"\n🔍 Тест несуществующего участника {fake_iin}...")
        
        try:
            params = {'participant_iin': fake_iin}
            
            response = requests.get(
                f"{self.base_url}/api/groups/my_groups/",
                headers=self.headers,
                params=params
            )
            
            data = response.json()
            print(f"   Статус: {response.status_code}")
            print(f"   Сообщение: {data.get('message')}")
            if 'details' in data:
                print(f"   Детали: {data['details']}")
            print(f"   Групп найдено: {data.get('total_groups', 0)}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка соединения: {e}")
    
    def test_pagination(self, participant_iin):
        """Тест пагинации"""
        print(f"\n📖 Тест пагинации для участника {participant_iin}...")
        
        # Получаем первую страницу с 2 элементами на странице
        data = self.test_my_groups(participant_iin, page=1, per_page=2)
        
        if data and data['pagination']['total_pages'] > 1:
            print("\n📖 Получение второй страницы...")
            self.test_my_groups(participant_iin, page=2, per_page=2)


def main():
    # Настройки (замените на ваши)
    BASE_URL = "http://localhost:8000"
    API_TOKEN = "your_api_token_here"  # Замените на реальный токен
    PARTICIPANT_IIN = "123456789012"   # Замените на реальный ИИН участника
    
    if len(sys.argv) > 1:
        API_TOKEN = sys.argv[1]
    if len(sys.argv) > 2:
        PARTICIPANT_IIN = sys.argv[2]
    
    if API_TOKEN == "your_api_token_here":
        print("❌ Необходимо указать API токен!")
        print("Использование: python test_api.py YOUR_TOKEN [PARTICIPANT_IIN]")
        print("\nИли отредактируйте переменные API_TOKEN и PARTICIPANT_IIN в скрипте")
        sys.exit(1)
    
    print("🚀 Тестирование API групп и посещаемости")
    print(f"   URL: {BASE_URL}")
    print(f"   Токен: {API_TOKEN[:10]}...")
    print(f"   ИИН участника: {PARTICIPANT_IIN}")
    print("=" * 60)
    
    client = APIClient(BASE_URL, API_TOKEN)
    
    # Тестируем API
    if client.test_health_check():
        # Основные тесты
        client.test_my_groups(PARTICIPANT_IIN)
        client.test_pagination(PARTICIPANT_IIN)
        
        # Тесты обработки ошибок
        print("\n" + "=" * 40)
        print("🧪 ТЕСТЫ ОБРАБОТКИ ОШИБОК")
        print("=" * 40)
        
        client.test_missing_parameter()
        client.test_nonexistent_participant()
    
    print("\n" + "=" * 60)
    print("✅ Тестирование завершено!")


if __name__ == "__main__":
    main() 