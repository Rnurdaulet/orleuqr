from django.db import models
from model_utils.models import TimeStampedModel
import secrets
import hashlib
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class BaseModel(TimeStampedModel):
    """
    Базовая модель с полями created и modified
    """
    class Meta:
        abstract = True


class APIToken(BaseModel):
    """
    Модель для API токенов доверенных сервисов
    """
    class Permission(models.TextChoices):
        READ_ONLY = "read_only", _("Только чтение")
        READ_WRITE = "read_write", _("Чтение и запись")
        ADMIN = "admin", _("Полный доступ")

    name = models.CharField(
        _("Название сервиса"), 
        max_length=100, 
        help_text=_("Описательное название для идентификации сервиса")
    )
    
    token_hash = models.CharField(
        _("Хэш токена"), 
        max_length=64, 
        unique=True,
        help_text=_("SHA-256 хэш токена для безопасного хранения")
    )
    
    prefix = models.CharField(
        _("Префикс токена"), 
        max_length=8,
        help_text=_("Первые символы токена для идентификации")
    )
    
    permissions = models.CharField(
        _("Уровень доступа"),
        max_length=20,
        choices=Permission.choices,
        default=Permission.READ_ONLY
    )
    
    is_active = models.BooleanField(
        _("Активен"), 
        default=True,
        help_text=_("Можно деактивировать токен без удаления")
    )
    
    last_used = models.DateTimeField(
        _("Последнее использование"), 
        null=True, 
        blank=True
    )
    
    expires_at = models.DateTimeField(
        _("Истекает"), 
        null=True, 
        blank=True,
        help_text=_("Оставьте пустым для токена без срока действия")
    )
    
    ip_whitelist = models.TextField(
        _("Белый список IP"), 
        blank=True,
        help_text=_("IP адреса через запятую. Пустое поле = доступ с любого IP")
    )
    
    description = models.TextField(
        _("Описание"), 
        blank=True,
        help_text=_("Дополнительная информация о назначении токена")
    )

    class Meta:
        verbose_name = _("API Токен")
        verbose_name_plural = _("API Токены")
        ordering = ['-created']

    def __str__(self):
        return f"{self.name} ({self.prefix}***)"

    @classmethod
    def generate_token(cls):
        """Генерирует новый токен"""
        token = secrets.token_urlsafe(32)  # 256-битный токен
        return token

    @classmethod
    def create_token(cls, name, permissions=Permission.READ_ONLY, **kwargs):
        """Создает новый API токен"""
        token = cls.generate_token()
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        prefix = token[:8]
        
        api_token = cls.objects.create(
            name=name,
            token_hash=token_hash,
            prefix=prefix,
            permissions=permissions,
            **kwargs
        )
        
        # Возвращаем токен только при создании
        return api_token, token

    def verify_token(self, token):
        """Проверяет соответствие токена"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return self.token_hash == token_hash

    def is_valid(self):
        """Проверяет валидность токена"""
        if not self.is_active:
            return False
        
        if self.expires_at and timezone.now() > self.expires_at:
            return False
            
        return True

    def check_ip_access(self, ip_address):
        """Проверяет доступ с IP адреса"""
        if not self.ip_whitelist.strip():
            return True  # Нет ограничений по IP
        
        allowed_ips = [ip.strip() for ip in self.ip_whitelist.split(',')]
        return ip_address in allowed_ips

    def update_last_used(self):
        """Обновляет время последнего использования"""
        self.last_used = timezone.now()
        self.save(update_fields=['last_used'])
