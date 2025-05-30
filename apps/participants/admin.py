from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import BrowserFingerprint, PersonProfile


@admin.register(PersonProfile)
class PersonProfileAdmin(ModelAdmin):
    list_display = ("full_name", "iin", "email", "role_display", "fingerprint_count")
    list_filter = ("role", "fingerprints__trust_score")
    search_fields = ("full_name", "iin", "email")
    ordering = ("full_name",)

    fieldsets = (
        ("Основная информация", {
            "fields": ("full_name", "iin", "email", "role"),
        }),
    )

    def role_display(self, obj):
        return obj.get_role_display()
    role_display.short_description = "Роль"

    def fingerprint_count(self, obj):
        return obj.fingerprints.count()
    fingerprint_count.short_description = "Отпечатков"

class BrowserFingerprintInline(TabularInline):
    model = BrowserFingerprint
    fields = (
        "fingerprint_hash",
        "user_agent",
        "first_seen",
        "last_seen",
        "trust_score",
        "trust_level_display",
    )
    readonly_fields = fields
    extra = 0
    show_change_link = True


@admin.register(BrowserFingerprint)
class BrowserFingerprintAdmin(ModelAdmin):
    list_display = (
        "profile",
        "fingerprint_hash",
        "trust_score",
        "trust_level_display",
        "first_seen",
        "last_seen",
    )
    list_filter = ("trust_score",)
    search_fields = (
        "fingerprint_hash",
        "user_agent",
        "profile__iin",
        "profile__full_name",
    )

    fieldsets = (
        ("Связь", {
            "fields": ("profile",),
        }),
        ("Информация об отпечатке", {
            "fields": (
                "fingerprint_hash",
                "user_agent",
                "first_seen",
                "last_seen",
            ),
        }),
        ("Доверие", {
            "fields": ("trust_score", "trust_level_display"),
        }),
    )
    readonly_fields = ("first_seen", "last_seen", "trust_level_display")

    def trust_level_display(self, obj):
        labels = dict(obj.TrustLevel.choices)
        return labels.get(obj.trust_level, obj.trust_level)

    trust_level_display.short_description = "Уровень доверия"
