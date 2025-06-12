from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import Attendance, TrustLog

@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    list_display = (
        "profile",
        "session",
        "arrived_at",
        "arrived_status_colored",    # Отображение статуса входа
        "left_at",
        "left_status_colored",       # Отображение статуса выхода
        "trust_level_colored",
        "trust_score",
        "marked_by_trainer",
    )
    list_filter = (
        "trust_level",
        "arrived_status",
        "left_status",
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
        "arrived_status",
        "left_status",
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

    def arrived_status_colored(self, obj):
        color_map = {
            "too_early": "orange",
            "on_time": "green",
            "too_late": "red",
            "unknown": "gray",
            "manual": "blue",
        }
        color = color_map.get(obj.arrived_status, "gray")
        return format_html(
            '<span style="color: {};">{}</span>', color, obj.get_arrived_status_display()
        )
    arrived_status_colored.short_description = "Статус входа"

    def left_status_colored(self, obj):
        color_map = {
            "too_early": "orange",
            "on_time": "green",
            "too_late": "red",
            "unknown": "gray",
            "manual": "blue",
        }
        color = color_map.get(obj.left_status, "gray")
        return format_html(
            '<span style="color: {};">{}</span>', color, obj.get_left_status_display()
        )
    left_status_colored.short_description = "Статус выхода"

@admin.register(TrustLog)
class TrustLogAdmin(ModelAdmin):
    list_display = ("fingerprint", "reason", "delta", "created_at")
    search_fields = ("reason", "fingerprint__fingerprint_hash")
    list_filter = ("created_at",)
