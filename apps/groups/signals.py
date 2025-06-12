from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Session
from .services import generate_session_qr_files

@receiver(post_save, sender=Session)
def generate_qr_pdfs_on_save(sender, instance, created, **kwargs):
    if created:
        # Генерируем QR только при создании сессии
        generate_session_qr_files(instance.id)
