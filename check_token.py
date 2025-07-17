#!/usr/bin/env python3
"""
Скрипт для проверки API токена
"""

import os
import sys
import django

# Добавляем путь проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orleuqr.settings')
django.setup()

from apps.core.models import APIToken

def check_token(token_value):
    """Проверяет статус API токена"""
    print(f"🔍 Проверяем токен: {token_value[:10]}...")
    
    try:
        # Ищем токен по префиксу
        prefix = token_value[:8]
        tokens = APIToken.objects.filter(prefix=prefix)
        
        if not tokens.exists():
            print(f"❌ Токен с префиксом '{prefix}' не найден в базе данных")
            return False
        
        for token in tokens:
            print(f"\n📋 Найден токен: {token.name}")
            print(f"   ID: {token.id}")
            print(f"   Префикс: {token.prefix}")
            print(f"   Активен: {'✅' if token.is_active else '❌'}")
            print(f"   Права: {token.permissions}")
            print(f"   Создан: {token.created_at}")
            print(f"   Последнее использование: {token.last_used or 'Никогда'}")
            print(f"   IP ограничения: {token.allowed_ips or 'Нет ограничений'}")
            
            # Проверяем токен
            if token.verify_token(token_value):
                print(f"   Верификация: ✅ Токен корректен")
                
                if token.is_valid():
                    print(f"   Валидность: ✅ Токен действителен")
                    print(f"\n🎉 Токен '{token.name}' работает корректно!")
                    return True
                else:
                    print(f"   Валидность: ❌ Токен истек или неактивен")
                    return False
            else:
                print(f"   Верификация: ❌ Токен не совпадает")
        
        return False
        
    except Exception as e:
        print(f"❌ Ошибка проверки токена: {e}")
        return False

def list_all_tokens():
    """Показывает все токены в системе"""
    print("\n📋 Все API токены в системе:")
    print("=" * 60)
    
    tokens = APIToken.objects.all().order_by('-created_at')
    
    if not tokens.exists():
        print("❌ В системе нет API токенов")
        print("\n💡 Создайте токен в админ панели:")
        print("   http://localhost:8000/admin/core/apitoken/")
        return
    
    for i, token in enumerate(tokens, 1):
        status = "✅" if token.is_active and token.is_valid() else "❌"
        print(f"{i}. {status} {token.name}")
        print(f"   Префикс: {token.prefix}")
        print(f"   Права: {token.permissions}")
        print(f"   Активен: {token.is_active}")
        if token.expires_at:
            print(f"   Истекает: {token.expires_at}")
        print()

def create_test_token():
    """Создает тестовый токен"""
    print("\n🔧 Создаем тестовый токен...")
    
    try:
        token = APIToken.objects.create(
            name="Test Token (auto-created)",
            permissions="read_write"
        )
        
        print(f"✅ Токен создан!")
        print(f"   Имя: {token.name}")
        print(f"   Токен: {token.key}")
        print(f"   Права: {token.permissions}")
        print("\n📝 Скопируйте этот токен в test_groups_api.py:")
        print(f"   API_TOKEN = '{token.key}'")
        
        return token.key
        
    except Exception as e:
        print(f"❌ Ошибка создания токена: {e}")
        return None

def main():
    print("🔐 Проверка API токенов")
    print("=" * 60)
    
    # Токен из тестового файла
    test_token = "Xou_3BhElBy8cCN53Gc3M7hjmPmhht_sZwwqZoCf1Qw"
    
    # Проверяем текущий токен
    if not check_token(test_token):
        print(f"\n❌ Токен {test_token[:10]}... не работает")
        
        # Показываем все токены
        list_all_tokens()
        
        # Предлагаем создать новый
        choice = input("\n❓ Создать новый тестовый токен? (y/n): ").lower().strip()
        if choice in ['y', 'yes', 'да', '']:
            new_token = create_test_token()
            if new_token:
                print(f"\n✅ Новый токен готов к использованию!")
        else:
            print("\n💡 Создайте токен вручную в админ панели:")
            print("   http://localhost:8000/admin/core/apitoken/")
    
    print("\n🏁 Проверка завершена")

if __name__ == "__main__":
    main() 