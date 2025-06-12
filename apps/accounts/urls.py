from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),              # /accounts/login/
    path('callback/', views.callback, name='callback'),          # /accounts/callback/
    path('logout/', views.logout, name='logout'),                # /accounts/logout/
]
