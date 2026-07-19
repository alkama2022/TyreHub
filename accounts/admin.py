"""
Django Admin configuration for Accounts & Audit Logging.

The AuditLog admin is intentionally read-only:
  - No adding entries manually
  - No editing existing entries
  - No deleting entries (audit trail must be immutable)

Only superusers can see the full audit log.
Staff users can only see their own activity.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import AuditLog


# ---------------------------------------------------------------------------
# Custom Filters
# ---------------------------------------------------------------------------

class ActionTypeFilter(admin.SimpleListFilter):
    title = "Action Type"
    parameter_name = "action_type"

    def lookups(self, request, model_admin):
        return AuditLog.ACTION_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(action=self.value())
        return queryset


# ---------------------------------------------------------------------------
# AuditLog Admin
# ---------------------------------------------------------------------------

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Read-only audit log viewer.

    Superusers see everything. Staff see only their own activity.
    """

    list_display = (
        "timestamp",
        "actor_display",
        "action_badge",
        "description_short",
        "target_info",
        "ip_address",
    )

    list_filter = (ActionTypeFilter, "timestamp")

    search_fields = (
        "actor__username",
        "actor_username",
        "description",
        "target_model",
        "ip_address",
    )

    date_hierarchy = "timestamp"

    ordering = ("-timestamp",)

    list_per_page = 50

    show_full_result_count = False

    readonly_fields = (
        "actor",
        "actor_username",
        "action",
        "description",
        "target_model",
        "target_id",
        "extra_data",
        "ip_address",
        "timestamp",
    )

    fieldsets = (
        ("Event Details", {
            "fields": ("timestamp", "action", "description"),
        }),
        ("Actor", {
            "fields": ("actor", "actor_username", "ip_address"),
        }),
        ("Target", {
            "fields": ("target_model", "target_id"),
        }),
        ("Extra Data", {
            "fields": ("extra_data",),
            "classes": ("collapse",),
        }),
    )

    # ------------------------------------------------------------------
    # Immutability enforcement
    # ------------------------------------------------------------------

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # ------------------------------------------------------------------
    # Queryset scoping
    # ------------------------------------------------------------------

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("actor")
        if request.user.is_superuser:
            return qs
        # Staff can only see their own audit trail
        return qs.filter(actor=request.user)

    # ------------------------------------------------------------------
    # List display callables
    # ------------------------------------------------------------------

    @admin.display(description="Actor", ordering="actor__username")
    def actor_display(self, obj):
        username = obj.actor_username or "Anonymous"
        if obj.actor:
            return format_html(
                '<strong>{}</strong>',
                username,
            )
        return format_html('<span style="color:#adb5bd;">{}</span>', username)

    @admin.display(description="Action", ordering="action")
    def action_badge(self, obj):
        colours = {
            "LOGIN":           ("#28a745", "✅"),
            "LOGOUT":          ("#6c757d", "🚪"),
            "LOGIN_FAILED":    ("#dc3545", "❌"),
            "PASSWORD_CHANGE": ("#fd7e14", "🔑"),
            "CREATE":          ("#0d6efd", "➕"),
            "UPDATE":          ("#17a2b8", "✏️"),
            "DELETE":          ("#dc3545", "🗑"),
            "DEACTIVATE":      ("#6c757d", "🚫"),
            "ACTIVATE":        ("#28a745", "✅"),
            "OTHER":           ("#6c757d", "ℹ️"),
        }
        colour, icon = colours.get(obj.action, ("#6c757d", "ℹ️"))
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; '
            'border-radius:10px; font-size:11px; font-weight:600;">{} {}</span>',
            colour, icon, obj.get_action_display(),
        )

    @admin.display(description="Description")
    def description_short(self, obj):
        text = obj.description
        if len(text) > 80:
            return text[:80] + "…"
        return text

    @admin.display(description="Target")
    def target_info(self, obj):
        if obj.target_model:
            if obj.target_id:
                return format_html(
                    '<code style="font-size:11px;">{} #{}</code>',
                    obj.target_model, obj.target_id,
                )
            return format_html(
                '<code style="font-size:11px;">{}</code>', obj.target_model
            )
        return "—"
