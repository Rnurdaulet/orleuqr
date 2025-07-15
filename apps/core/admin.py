from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.decorators import display
from .models import APIToken

@admin.register(APIToken)
class APITokenAdmin(ModelAdmin):
    list_display = [
        'name', 
        'prefix_display', 
        'permissions_display',
        'status_display', 
        'last_used_display',
        'expires_display',
        'created'
    ]
    
    list_filter = [
        'permissions', 
        'is_active',
        ('created', RangeDateFilter),
        ('last_used', RangeDateFilter),
        ('expires_at', RangeDateFilter),
    ]
    
    search_fields = ['name', 'description', 'prefix']
    
    readonly_fields = [
        'token_hash', 
        'prefix', 
        'created', 
        'modified', 
        'last_used'
    ]
    
    # Настройки Unfold
    compressed_fields = True
    warn_unsaved_form = True
    show_full_result_count = False
    list_per_page = 25
    
    # Действия
    actions = ['deactivate_tokens', 'activate_tokens']
    
    def get_fieldsets(self, request, obj=None):
        if obj:  # При редактировании существующего токена
            return (
                (_("Основная информация"), {
                    'fields': ('name', 'description', 'permissions')
                }),
                (_("Настройки доступа"), {
                    'fields': ('is_active', 'expires_at', 'ip_whitelist')
                }),
                (_("Техническая информация"), {
                    'fields': ('prefix', 'token_hash', 'last_used', 'created', 'modified'),
                    'classes': ('collapse',)
                }),
            )
        else:  # При создании нового токена
            return (
                (_("Основная информация"), {
                    'fields': ('name', 'description', 'permissions')
                }),
                (_("Настройки доступа"), {
                    'fields': ('is_active', 'expires_at', 'ip_whitelist')
                }),
            )
    
    @display(description=_("Токен"))
    def prefix_display(self, obj):
        return format_html(
            '<code style="background: #f8f9fa; padding: 2px 6px; border-radius: 3px;">{}</code>',
            f"{obj.prefix}***"
        )
    
    @display(description=_("Права доступа"))
    def permissions_display(self, obj):
        colors = {
            'read_only': '#28a745',    # зеленый
            'read_write': '#ffc107',   # желтый  
            'admin': '#dc3545'         # красный
        }
        color = colors.get(obj.permissions, '#6c757d')
        
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_permissions_display()
        )
    
    @display(description=_("Статус"))
    def status_display(self, obj):
        if obj.is_active and obj.is_valid():
            return format_html(
                '<span style="color: #28a745;">●</span> <span style="color: #28a745; font-weight: bold;">Активен</span>'
            )
        elif obj.is_active and not obj.is_valid():
            return format_html(
                '<span style="color: #ffc107;">●</span> <span style="color: #ffc107; font-weight: bold;">Истек</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545;">●</span> <span style="color: #dc3545; font-weight: bold;">Отключен</span>'
            )
    
    @display(description=_("Последнее использование"))
    def last_used_display(self, obj):
        if obj.last_used:
            return obj.last_used.strftime('%d.%m.%Y %H:%M')
        return format_html('<span style="color: #6c757d; font-style: italic;">Никогда</span>')
    
    @display(description=_("Истекает"))
    def expires_display(self, obj):
        if obj.expires_at:
            return obj.expires_at.strftime('%d.%m.%Y %H:%M')
        return format_html('<span style="color: #6c757d; font-style: italic;">Никогда</span>')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # При редактировании
            return self.readonly_fields
        else:  # При создании
            return ['token_hash', 'prefix', 'last_used']
    
    def save_model(self, request, obj, form, change):
        if not change:  # При создании нового токена
            # Генерируем токен и заполняем поля, но НЕ сохраняем в базу
            token = APIToken.generate_token()
            import hashlib
            obj.token_hash = hashlib.sha256(token.encode()).hexdigest()
            obj.prefix = token[:8]
            
            # Сохраняем объект через Django ORM
            super().save_model(request, obj, form, change)
            
            # Показываем токен пользователю
            self.message_user(
                request,
                format_html(
                    '<div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 6px; padding: 16px; margin: 8px 0;">'
                    '<div style="display: flex; align-items: center; margin-bottom: 12px;">'
                    '<span style="color: #856404; font-size: 18px; margin-right: 8px;">🔑</span>'
                    '<strong style="color: #856404;">API Токен успешно создан</strong>'
                    '</div>'
                    '<div style="margin-bottom: 8px;">'
                    '<strong>Ваш токен:</strong><br>'
                    '<code style="background: #f8f9fa; padding: 8px 12px; border-radius: 4px; '
                    'font-family: monospace; font-size: 14px; word-break: break-all; display: block; margin: 4px 0;">{}</code>'
                    '</div>'
                    '<div style="color: #721c24; background: #f8d7da; border: 1px solid #f5c6cb; '
                    'border-radius: 4px; padding: 8px; font-size: 13px;">'
                    '<strong>⚠️ ВАЖНО:</strong> Сохраните токен сейчас! Вы больше не сможете его увидеть.'
                    '</div>'
                    '</div>',
                    token
                ),
                level='WARNING'
            )
        else:
            # При редактировании существующего токена
            super().save_model(request, obj, form, change)
    
    @admin.action(description=_("Деактивировать выбранные токены"))
    def deactivate_tokens(self, request, queryset):
        updated = queryset.filter(is_active=True).update(is_active=False)
        self.message_user(
            request,
            format_html(_("Деактивировано токенов: <strong>{}</strong>"), updated),
            level='SUCCESS'
        )
    
    @admin.action(description=_("Активировать выбранные токены"))
    def activate_tokens(self, request, queryset):
        updated = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(
            request,
            format_html(_("Активировано токенов: <strong>{}</strong>"), updated),
            level='SUCCESS'
        )
