from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    list_display = (
        "session_display",
        "profile",
        "trust_level_colored",
        "trust_score",
        "marked_by_trainer",
        "timestamp"
    )
    list_filter = (
        "trust_level",
        "session__group__code",
        "session__date",
        "marked_by_trainer",
    )
    search_fields = (
        "profile__full_name",
        "profile__iin",
        "session__group__code",
        "fingerprint_hash",
    )
    readonly_fields = (
        "session", "profile", "fingerprint_hash", "timestamp", "marked_by_trainer", "trust_level", "trust_score"
    )

    fieldsets = (
        ("Основное", {
            "fields": ("session", "profile", "timestamp"),
        }),
        ("Идентификация", {
            "fields": ("fingerprint_hash",),
        }),
        ("Доверие", {
            "fields": ("trust_score", "trust_level", "marked_by_trainer"),
        }),
    )

    def session_display(self, obj):
        return f"{obj.session.group.code} — {obj.session.date}"
    session_display.short_description = "Сессия"

    def trust_level_colored(self, obj):
        color = {
            "trusted": "green",
            "suspicious": "orange",
            "blocked": "red",
        }.get(obj.trust_level, "gray")
        return f'<span style="color:{color}; font-weight:bold;">{obj.get_trust_level_display()}</span>'
    trust_level_colored.short_description = "Доверие"
    trust_level_colored.allow_tags = True
