from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.shortcuts import render
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import home_view

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    path("", home_view, name='home'),
    path('accounts/', include('apps.accounts.urls')),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("qr/", include("apps.qr.urls")),
    path("attendance/", include("apps.attendance.urls", namespace="attendance")),

    path("groups/", include("apps.groups.urls", namespace="groups")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path("privacy", lambda request: render(request, "privacy.html"), name="privacy"),
    path("404", lambda request: render(request, "404.html"), name="404"),
)
