import segno
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.timezone import localtime
from django.conf import settings
from apps.groups.models import Session
from apps.logger import logger


def generate_session_qr_files(session_id):
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        logger.error(f"Session with id={session_id} does not exist.")
        return False

    try:
        base_url = settings.SITE_BASE_URL.rstrip('/')

        mark_url = f"{base_url}/qr/mark/{session.qr_token_entry}/"
        leave_url = f"{base_url}/qr/leave/{session.qr_token_exit}/"

        # SVG QR вход
        buffer_entry = BytesIO()
        qr_entry = segno.make(mark_url)
        qr_entry.save(buffer_entry, kind='svg')
        buffer_entry.seek(0)
        filename_entry = f"{session.id}_entry_{localtime().strftime('%Y%m%d')}.svg"
        session.qr_file_entry.save(filename_entry, ContentFile(buffer_entry.read()), save=False)

        # SVG QR выход - только если группа отслеживает выход
        if session.group.track_exit:
            buffer_exit = BytesIO()
            qr_exit = segno.make(leave_url)
            qr_exit.save(buffer_exit, kind='svg')
            buffer_exit.seek(0)
            filename_exit = f"{session.id}_exit_{localtime().strftime('%Y%m%d')}.svg"
            session.qr_file_exit.save(filename_exit, ContentFile(buffer_exit.read()), save=False)

        session.save()
        logger.info(f"SVG QR-codes generated and saved for session id={session_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to generate QR SVGs for session id={session_id}: {e}", exc_info=True)
        return False


import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Папка с services.py
FONT_PATH = os.path.join(BASE_DIR, 'DejaVuSans.ttf')

from django.utils.translation import gettext as _
from io import BytesIO
import segno
from django.conf import settings
from django.utils.timezone import localtime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader


def generate_session_qr_pdf_on_fly(session_id, mode='entry'):
    """
    Генерация PDF с QR и инфо для печати, возвращает bytes PDF или None при ошибке.
    Только для course_name выполняется автоматический перенос.
    """
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        logger.error(f"Session with id={session_id} does not exist.")
        return None

    # Проверяем, разрешен ли выход для этой группы
    if mode == 'exit' and not session.group.track_exit:
        logger.warning(f"Exit tracking is disabled for group {session.group.code}")
        return None

    # Собираем URL для QR
    base_url = getattr(settings, "SITE_BASE_URL", "http://127.0.0.1:8000").rstrip('/')
    token = session.qr_token_entry if mode == 'entry' else session.qr_token_exit
    qr_url = f"{base_url}/qr/{'mark' if mode == 'entry' else 'leave'}/{token}/"

    # Рисуем QR в память
    buf_qr = BytesIO()
    segno.make(qr_url).save(buf_qr, kind='png', scale=8)
    buf_qr.seek(0)
    qr_img = ImageReader(buf_qr)

    # Подготовка PDF
    output = BytesIO()
    c = canvas.Canvas(output, pagesize=A4)

    # Регистрируем шрифт
    pdfmetrics.registerFont(TTFont('DejaVu', FONT_PATH))
    c.setFont('DejaVu', 14)

    width, height = A4
    margin = 20 * mm

    # Размер и позиция QR
    qr_size = 150 * mm
    qr_x = (width - qr_size) / 2
    qr_y = height - margin - qr_size
    c.drawImage(qr_img, qr_x, qr_y, qr_size, qr_size)

    # Код группы
    text_y = qr_y - 20
    c.setFont('DejaVu', 26)
    c.drawCentredString(width / 2, text_y, session.group.code)

    # Название курса с переносом
    text_y -= 24
    style = ParagraphStyle(
        name='CourseName',
        fontName='DejaVu',
        fontSize=26,
        leading=24,
        alignment=TA_CENTER,
    )
    para = Paragraph(session.group.course_name, style)
    # оборачиваем в ширину чуть меньше страницы (оставляем поля)
    w, h = para.wrap(width - 2 * margin, height)
    para.drawOn(c, margin, text_y - h)

    # корректируем позицию для следующих строк
    text_y = text_y - h - 30

    # Дата и время
    date_str = session.date.strftime('%d.%m.%Y')
    c.setFont('DejaVu', 14)
    c.drawCentredString(width / 2, text_y, date_str)
    start_time = session.entry_start if mode == 'entry' else session.exit_start
    text_y -= 18
    c.drawCentredString(width / 2, text_y, start_time.strftime('%H:%M'))

    # Тип
    text_y -= 30
    c.setFont('DejaVu', 16)
    c.drawCentredString(width / 2, text_y, _("Вход") if mode == 'entry' else _("Выход"))

    c.showPage()
    c.save()
    output.seek(0)
    return output.read()
