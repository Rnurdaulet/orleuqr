from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Group, Session


class SessionInline(TabularInline):
    model = Session
    extra = 0
    show_change_link = True
    fields = ("date", "start_time", "end_time", "qr_token")
    readonly_fields = ("qr_token",)
    ordering = ("date",)


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    list_display = ("code", "course_name_short", "supervisor_name", "start_date", "end_date", "participant_count")
    search_fields = ("code", "course_name", "supervisor_name", "supervisor_iin")
    list_filter = ("start_date", "end_date")
    inlines = [SessionInline]

    filter_horizontal = ("participants", "trainers")

    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = "Участников"

    def course_name_short(self, obj):
        return obj.course_name[:64] + "..." if len(obj.course_name) > 64 else obj.course_name
    course_name_short.short_description = "Название курса"

    fieldsets = (
        ("Основное", {
            "fields": ("external_id", "code", "course_name", "supervisor_name", "supervisor_iin")
        }),
        ("Даты", {
            "fields": ("start_date", "end_date")
        }),
        ("Связи", {
            "fields": ("participants", "trainers")
        }),
    )


@admin.register(Session)
class SessionAdmin(ModelAdmin):
    list_display = ("group", "date", "start_time", "end_time", "qr_token")
    search_fields = ("group__code",)
    list_filter = ("group__code", "date")
    readonly_fields = ("qr_token",)

    fieldsets = (
        ("Сессия", {
            "fields": ("group", "date", "start_time", "end_time", "qr_token")
        }),
    )
