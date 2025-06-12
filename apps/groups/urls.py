from django.urls import path
from .views import my_groups_view, session_qr_pdf_view

app_name = "groups"

urlpatterns = [
    path("my/", my_groups_view, name="my_groups"),
    path('session/<int:session_id>/qr-pdf/', session_qr_pdf_view, name='session_qr_pdf'),
]
