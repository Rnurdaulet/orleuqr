from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    list_display = (
        "profile",
        "session",
        "arrived_at",
        "left_at",
        "trust_level_colored",
        "trust_score",
        "marked_by_trainer",
    )
    list_filter = (
        "trust_level",
        "session__group__code",
        "session__date",
        "marked_by_trainer",
    )
    search_fields = (
        "profile__iin",
        "profile__full_name",
        "session__group__code",
    )
    readonly_fields = (
        "session",
        "profile",
        "arrived_at",
        "left_at",
        "fingerprint_hash",
        "trust_level",
        "trust_score",
        "marked_by_trainer",
        "created_at",
    )
    ordering = ("-arrived_at",)

    def trust_level_colored(self, obj):
        color = {
            "trusted": "green",
            "suspicious": "orange",
            "blocked": "red"
        }.get(obj.trust_level, "gray")
        return format_html(
            '<span style="color: {};">{}</span>', color, obj.get_trust_level_display()
        )
    trust_level_colored.short_description = "Доверие"
