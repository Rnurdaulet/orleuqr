from django.urls import path
from . import views

urlpatterns = [
    path("manual-mark/", views.manual_mark_view, name="manual_mark"),
]
