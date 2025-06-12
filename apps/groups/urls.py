from django.urls import path
from .views import my_groups_view

app_name = "groups"

urlpatterns = [
    path("my/", my_groups_view, name="my_groups"),
]
