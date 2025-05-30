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
    )
    list_filter = ("group__code", "date")
    search_fields = ("group__code",)
    ordering = ("-date",)

    readonly_fields = (
        "qr_token_entry",
        "qr_token_exit",
    )

    fieldsets = (
        ("Основная информация", {
            "fields": ("group", "date")
        }),
        ("Вход", {
            "fields": ("entry_start", "entry_end", "qr_token_entry")
        }),
        ("Выход", {
            "fields": ("exit_start", "exit_end", "qr_token_exit")
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
