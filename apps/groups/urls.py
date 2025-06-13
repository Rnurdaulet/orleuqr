from django.urls import path
from .views import (
    participant_groups_view,
    trainer_groups_view,
    group_detail_view,
    session_qr_pdf_view, manual_attendance_data, attendance_json_view
)

app_name = "groups"

urlpatterns = [
    path("my/", participant_groups_view, name="my_groups"),
    path("manage/", trainer_groups_view, name="trainer_groups"),
    path("<int:group_id>/", group_detail_view, name="group_detail"),
    path("<int:group_id>/attendance.json", attendance_json_view, name="attendance_json"),

    path("<int:group_id>/manual-attendance/<int:participant_id>/", manual_attendance_data,
         name="manual_attendance_data"),
    path('session/<int:session_id>/qr-pdf/', session_qr_pdf_view, name='session_qr_pdf'),
]
