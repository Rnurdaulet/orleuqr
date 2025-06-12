from django.urls import path

from . import views
from .views import mark_qr_page, mark_qr_exit_page

urlpatterns = [
    path("mark/<uuid:token>/", mark_qr_page, name="mark_qr"),
    path("leave/<uuid:token>/", mark_qr_exit_page, name="qr_mark_exit"),
    path("scan/", views.qr_scan_page, name="qr_scan"),
]
