from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
from apps.core.models import APIToken


class Command(BaseCommand):
    help = 'Управление API токенами для доверенных сервисов'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Доступные действия')
        
        # Создание токена
        create_parser = subparsers.add_parser('create', help='Создать новый API токен')
        create_parser.add_argument('name', help='Название сервиса')
        create_parser.add_argument(
            '--permissions', 
            choices=['read_only', 'read_write', 'admin'],
            default='read_only',
            help='Уровень доступа (по умолчанию: read_only)'
        )
        create_parser.add_argument(
            '--expires-days', 
            type=int,
            help='Срок действия в днях (по умолчанию: без срока)'
        )
        create_parser.add_argument(
            '--ip-whitelist',
            help='Разрешенные IP адреса через запятую'
        )
        create_parser.add_argument(
            '--description',
            help='Описание назначения токена'
        )
        
        # Список токенов
        list_parser = subparsers.add_parser('list', help='Показать все токены')
        list_parser.add_argument(
            '--active-only',
            action='store_true',
            help='Показать только активные токены'
        )
        
        # Деактивация токена
        deactivate_parser = subparsers.add_parser('deactivate', help='Деактивировать токен')
        deactivate_parser.add_argument('token_id', type=int, help='ID токена')
        
        # Активация токена
        activate_parser = subparsers.add_parser('activate', help='Активировать токен')
        activate_parser.add_argument('token_id', type=int, help='ID токена')
        
        # Удаление токена
        delete_parser = subparsers.add_parser('delete', help='Удалить токен')
        delete_parser.add_argument('token_id', type=int, help='ID токена')
        delete_parser.add_argument(
            '--confirm',
            action='store_true',
            help='Подтвердить удаление'
        )
        
        # Информация о токене
        info_parser = subparsers.add_parser('info', help='Показать информацию о токене')
        info_parser.add_argument('token_id', type=int, help='ID токена')

    def handle(self, *args, **options):
        action = options.get('action')
        
        if action == 'create':
            self.create_token(options)
        elif action == 'list':
            self.list_tokens(options)
        elif action == 'deactivate':
            self.deactivate_token(options)
        elif action == 'activate':
            self.activate_token(options)
        elif action == 'delete':
            self.delete_token(options)
        elif action == 'info':
            self.show_token_info(options)
        else:
            self.print_help('manage_api_tokens', '')

    def create_token(self, options):
        """Создает новый API токен"""
        name = options['name']
        permissions = options['permissions']
        
        # Подготавливаем параметры
        token_params = {
            'permissions': permissions,
        }
        
        if options.get('expires_days'):
            token_params['expires_at'] = timezone.now() + timedelta(days=options['expires_days'])
        
        if options.get('ip_whitelist'):
            token_params['ip_whitelist'] = options['ip_whitelist']
            
        if options.get('description'):
            token_params['description'] = options['description']
        
        try:
            api_token, token = APIToken.create_token(name, **token_params)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Токен успешно создан!')
            )
            self.stdout.write(f'ID: {api_token.id}')
            self.stdout.write(f'Название: {api_token.name}')
            self.stdout.write(f'Права доступа: {api_token.get_permissions_display()}')
            
            if api_token.expires_at:
                self.stdout.write(f'Истекает: {api_token.expires_at.strftime("%d.%m.%Y %H:%M")}')
            else:
                self.stdout.write('Истекает: Никогда')
                
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.WARNING('🔑 ВАШ API ТОКЕН:'))
            self.stdout.write(self.style.HTTP_NOT_MODIFIED(token))
            self.stdout.write('='*60)
            self.stdout.write(
                self.style.ERROR(
                    '⚠️  ВАЖНО: Сохраните токен сейчас!\n'
                    'Вы больше не сможете его увидеть.'
                )
            )
            
        except Exception as e:
            raise CommandError(f'Ошибка при создании токена: {str(e)}')

    def list_tokens(self, options):
        """Показывает список всех токенов"""
        queryset = APIToken.objects.all()
        
        if options.get('active_only'):
            queryset = queryset.filter(is_active=True)
            
        tokens = queryset.order_by('-created')
        
        if not tokens.exists():
            self.stdout.write('Токены не найдены.')
            return
        
        self.stdout.write(f'📋 Найдено токенов: {tokens.count()}\n')
        
        for token in tokens:
            status = '✅' if token.is_active else '❌'
            valid = '🟢' if token.is_valid() else '🔴'
            
            self.stdout.write(f'{status} {valid} ID: {token.id} | {token.name}')
            self.stdout.write(f'   Префикс: {token.prefix}***')
            self.stdout.write(f'   Права: {token.get_permissions_display()}')
            self.stdout.write(f'   Создан: {token.created.strftime("%d.%m.%Y %H:%M")}')
            
            if token.last_used:
                self.stdout.write(f'   Последнее использование: {token.last_used.strftime("%d.%m.%Y %H:%M")}')
            else:
                self.stdout.write('   Последнее использование: Никогда')
                
            if token.expires_at:
                self.stdout.write(f'   Истекает: {token.expires_at.strftime("%d.%m.%Y %H:%M")}')
            
            if token.ip_whitelist:
                self.stdout.write(f'   IP ограничения: {token.ip_whitelist}')
                
            self.stdout.write('')

    def deactivate_token(self, options):
        """Деактивирует токен"""
        token_id = options['token_id']
        
        try:
            token = APIToken.objects.get(id=token_id)
            if not token.is_active:
                self.stdout.write(self.style.WARNING(f'Токен {token.name} уже деактивирован.'))
                return
                
            token.is_active = False
            token.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Токен {token.name} успешно деактивирован.')
            )
            
        except APIToken.DoesNotExist:
            raise CommandError(f'Токен с ID {token_id} не найден.')

    def activate_token(self, options):
        """Активирует токен"""
        token_id = options['token_id']
        
        try:
            token = APIToken.objects.get(id=token_id)
            if token.is_active:
                self.stdout.write(self.style.WARNING(f'Токен {token.name} уже активен.'))
                return
                
            token.is_active = True
            token.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Токен {token.name} успешно активирован.')
            )
            
        except APIToken.DoesNotExist:
            raise CommandError(f'Токен с ID {token_id} не найден.')

    def delete_token(self, options):
        """Удаляет токен"""
        token_id = options['token_id']
        
        if not options.get('confirm'):
            raise CommandError(
                'Удаление токена необратимо. '
                'Используйте флаг --confirm для подтверждения.'
            )
        
        try:
            token = APIToken.objects.get(id=token_id)
            token_name = token.name
            token.delete()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Токен {token_name} успешно удален.')
            )
            
        except APIToken.DoesNotExist:
            raise CommandError(f'Токен с ID {token_id} не найден.')

    def show_token_info(self, options):
        """Показывает подробную информацию о токене"""
        token_id = options['token_id']
        
        try:
            token = APIToken.objects.get(id=token_id)
            
            self.stdout.write(f'📋 Информация о токене')
            self.stdout.write('='*40)
            self.stdout.write(f'ID: {token.id}')
            self.stdout.write(f'Название: {token.name}')
            self.stdout.write(f'Префикс: {token.prefix}***')
            self.stdout.write(f'Права доступа: {token.get_permissions_display()}')
            self.stdout.write(f'Статус: {"Активен" if token.is_active else "Деактивирован"}')
            self.stdout.write(f'Валидность: {"Действителен" if token.is_valid() else "Недействителен"}')
            
            self.stdout.write(f'Создан: {token.created.strftime("%d.%m.%Y %H:%M")}')
            self.stdout.write(f'Изменен: {token.modified.strftime("%d.%m.%Y %H:%M")}')
            
            if token.last_used:
                self.stdout.write(f'Последнее использование: {token.last_used.strftime("%d.%m.%Y %H:%M")}')
            else:
                self.stdout.write('Последнее использование: Никогда')
            
            if token.expires_at:
                self.stdout.write(f'Истекает: {token.expires_at.strftime("%d.%m.%Y %H:%M")}')
                if token.expires_at < timezone.now():
                    self.stdout.write(self.style.ERROR('⚠️  Токен истек!'))
            else:
                self.stdout.write('Истекает: Никогда')
            
            if token.ip_whitelist:
                self.stdout.write(f'IP ограничения: {token.ip_whitelist}')
            else:
                self.stdout.write('IP ограничения: Нет')
            
            if token.description:
                self.stdout.write(f'Описание: {token.description}')
                
        except APIToken.DoesNotExist:
            raise CommandError(f'Токен с ID {token_id} не найден.') 