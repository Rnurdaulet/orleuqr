from django.urls import path
from .views import manual_mark_view

app_name = "attendance"

urlpatterns = [
    path("manual/", manual_mark_view, name="manual_mark"),
]
