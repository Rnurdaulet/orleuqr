from django.urls import path
from . import views

urlpatterns = [
    path("mark/<uuid:token>/", views.mark_qr_page, name="mark_qr"),
]
