from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Group, Session

@admin.register(Group)
class GroupAdmin(ModelAdmin):
    list_display = ("code", "course_name_short", "supervisor_name", "start_date", "end_date", "participant_count")
    search_fields = ("code", "course_name", "supervisor_name", "supervisor_iin")
    list_filter = ("start_date", "end_date")

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
        ("Настройки отметок", {
            "fields": ("use_time_limits", "track_exit"),
            "description": "Настройки ограничений по времени отметок участников",
        }),
        ("Связи", {
            "fields": ("participants", "trainers")
        }),
    )


from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Group, Session


@admin.register(Session)
class SessionAdmin(ModelAdmin):
    list_display = (
        "group",
        "date",
        "entry_window",
        "exit_window",
        "qr_token_entry_short",
        "qr_token_exit_short",
        "qr_file_entry_link",
        "qr_file_exit_link",
    )
    list_filter = ("group__code", "date")
    search_fields = ("group__code",)
    ordering = ("-date",)

    readonly_fields = (
        "qr_token_entry",
        "qr_token_exit",
        "qr_file_entry",
        "qr_file_exit",
    )

    fieldsets = (
        ("Основная информация", {
            "fields": ("group", "date")
        }),
        ("Вход", {
            "fields": ("entry_start", "entry_end", "qr_token_entry", "qr_file_entry")
        }),
        ("Выход", {
            "fields": ("exit_start", "exit_end", "qr_token_exit", "qr_file_exit")
        }),
    )

    def entry_window(self, obj):
        return f"{obj.entry_start} – {obj.entry_end}"
    entry_window.short_description = "Окно входа"

    def exit_window(self, obj):
        return f"{obj.exit_start} – {obj.exit_end}"
    exit_window.short_description = "Окно выхода"

    def qr_token_entry_short(self, obj):
        return str(obj.qr_token_entry)[:8]
    qr_token_entry_short.short_description = "QR (вход)"

    def qr_token_exit_short(self, obj):
        return str(obj.qr_token_exit)[:8]
    qr_token_exit_short.short_description = "QR (выход)"

    def qr_file_entry_link(self, obj):
        if obj.qr_file_entry:
            return f'<a href="{obj.qr_file_entry.url}" target="_blank">Скачать PDF</a>'
        return "-"
    qr_file_entry_link.allow_tags = True
    qr_file_entry_link.short_description = "PDF вход"

    def qr_file_exit_link(self, obj):
        if obj.qr_file_exit:
            return f'<a href="{obj.qr_file_exit.url}" target="_blank">Скачать PDF</a>'
        return "-"
    qr_file_exit_link.allow_tags = True
    qr_file_exit_link.short_description = "PDF выход"