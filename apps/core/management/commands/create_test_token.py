from django.core.management.base import BaseCommand
from apps.core.models import APIToken


class Command(BaseCommand):
    help = 'Создает тестовый API токен для разработки'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            default='Test Token (Development)',
            help='Название токена'
        )
        parser.add_argument(
            '--permissions',
            type=str,
            default='read_write',
            choices=['read_only', 'read_write', 'admin'],
            help='Уровень прав доступа'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Пересоздать токен если он уже существует'
        )

    def handle(self, *args, **options):
        name = options['name']
        permissions = options['permissions']
        force = options['force']
        
        # Проверяем, существует ли уже токен с таким именем
        existing_token = APIToken.objects.filter(name=name).first()
        
        if existing_token and not force:
            self.stdout.write(
                self.style.WARNING(
                    f'Токен "{name}" уже существует.\n'
                    f'Токен: {existing_token.key}\n'
                    f'Используйте --force для пересоздания.'
                )
            )
            return
        
        if existing_token and force:
            existing_token.delete()
            self.stdout.write(
                self.style.WARNING(f'Удален существующий токен "{name}"')
            )
        
        # Создаем новый токен
        try:
            token = APIToken.objects.create(
                name=name,
                permissions=permissions
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Токен успешно создан!\n'
                    f'Имя: {token.name}\n'
                    f'Права: {token.permissions}\n'
                    f'Токен: {token.key}\n\n'
                    f'📝 Скопируйте этот токен в test_groups_api.py:\n'
                    f'API_TOKEN = \'{token.key}\'\n\n'
                    f'Или установите переменную окружения:\n'
                    f'export API_TOKEN={token.key}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка создания токена: {e}')
            ) 