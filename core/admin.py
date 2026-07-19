"""
Professional Django Admin configuration for TyreHub User Management.

Features:
  - Full user list with role badge, status indicators, dates
  - Organised fieldsets with profile section
  - Bulk activate/deactivate/export actions
  - Recent audit log inline on user detail
  - Password management via Django's built-in secure flow
  - Staff-only admin enforcement
"""

import csv

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import User


# ---------------------------------------------------------------------------
# Inline: Recent Audit Logs on User Detail Page
# ---------------------------------------------------------------------------

class RecentAuditLogInline(admin.TabularInline):
    """
    Shows the 10 most recent audit log entries for this user.
    """
    from accounts.models import AuditLog
    model = AuditLog
    fk_name = "actor"
    verbose_name = "Recent Activity"
    verbose_name_plural = "Recent Activity (last 10 entries)"
    extra = 0
    max_num = 0              # No adding new entries from here
    can_delete = False       # Audit logs are immutable

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by("-timestamp")[:10]

    def get_fields(self, request, obj=None):
        return ("timestamp", "action_display", "description", "ip_address")

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    readonly_fields = ("timestamp", "action_display", "description", "ip_address")

    @admin.display(description="Action")
    def action_display(self, obj):
        colours = {
            "LOGIN":           "#28a745",
            "LOGOUT":          "#6c757d",
            "LOGIN_FAILED":    "#dc3545",
            "PASSWORD_CHANGE": "#fd7e14",
            "CREATE":          "#007bff",
            "UPDATE":          "#17a2b8",
            "DELETE":          "#dc3545",
            "DEACTIVATE":      "#6c757d",
            "ACTIVATE":        "#28a745",
        }
        colour = colours.get(obj.action, "#6c757d")
        return format_html(
            '<span style="color:white; background:{}; padding:2px 8px; '
            'border-radius:10px; font-size:11px; font-weight:600;">{}</span>',
            colour,
            obj.get_action_display(),
        )


# ---------------------------------------------------------------------------
# Admin Actions
# ---------------------------------------------------------------------------

@admin.action(description="✅ Activate selected users")
def activate_users(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(
        request, f"{updated} user(s) successfully activated.", messages.SUCCESS
    )


@admin.action(description="🚫 Deactivate selected users")
def deactivate_users(modeladmin, request, queryset):
    # Prevent self-deactivation
    queryset = queryset.exclude(pk=request.user.pk)
    updated = queryset.update(is_active=False)
    modeladmin.message_user(
        request, f"{updated} user(s) deactivated.", messages.WARNING
    )


@admin.action(description="📥 Export selected users to CSV")
def export_users_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="tyrerhub_users_{timezone.now():%Y%m%d_%H%M}.csv"'
    )
    writer = csv.writer(response)
    writer.writerow([
        "ID", "Username", "Email", "First Name", "Last Name",
        "Staff", "Active", "Superuser", "Date Joined", "Last Login",
    ])
    for u in queryset.select_related():
        writer.writerow([
            u.id, u.username, u.email, u.first_name, u.last_name,
            u.is_staff, u.is_active, u.is_superuser,
            u.date_joined.strftime("%Y-%m-%d %H:%M") if u.date_joined else "",
            u.last_login.strftime("%Y-%m-%d %H:%M") if u.last_login else "Never",
        ])
    return response


# ---------------------------------------------------------------------------
# Custom List Filters
# ---------------------------------------------------------------------------

class RecentlyJoinedFilter(admin.SimpleListFilter):
    """Filter users who joined in the last 7 days."""
    title = "Recently Joined"
    parameter_name = "recently_joined"

    def lookups(self, request, model_admin):
        return [
            ("7d",  "Last 7 days"),
            ("30d", "Last 30 days"),
            ("90d", "Last 90 days"),
        ]

    def queryset(self, request, queryset):
        now = timezone.now()
        days_map = {"7d": 7, "30d": 30, "90d": 90}
        days = days_map.get(self.value())
        if days:
            return queryset.filter(date_joined__gte=now - timezone.timedelta(days=days))
        return queryset


class LoginStatusFilter(admin.SimpleListFilter):
    """Filter users based on whether they have ever logged in."""
    title = "Login Status"
    parameter_name = "login_status"

    def lookups(self, request, model_admin):
        return [
            ("logged_in",  "Has logged in"),
            ("never",      "Never logged in"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "logged_in":
            return queryset.filter(last_login__isnull=False)
        if self.value() == "never":
            return queryset.filter(last_login__isnull=True)
        return queryset


# ---------------------------------------------------------------------------
# Main UserAdmin
# ---------------------------------------------------------------------------

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Professional User management in Django Admin.

    Provides full CRUD, role visibility, bulk actions, and audit log inline.
    Password management uses Django's built-in secure hashed flow.
    """

    model = User

    # ------------------------------------------------------------------
    # List view configuration
    # ------------------------------------------------------------------

    list_display = (
        "avatar_thumbnail",
        "username",
        "full_name",
        "email",
        "role_badge",
        "is_active_badge",
        "date_joined_display",
        "last_login_display",
    )

    list_display_links = ("username", "full_name")

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
        RecentlyJoinedFilter,
        LoginStatusFilter,
    )

    search_fields = ("username", "email", "first_name", "last_name", "phone_number")

    ordering = ("-date_joined",)

    list_per_page = 25

    list_select_related = True

    show_full_result_count = False   # Avoids slow COUNT(*) on large tables

    actions = [activate_users, deactivate_users, export_users_csv]

    # ------------------------------------------------------------------
    # Detail / edit view configuration
    # ------------------------------------------------------------------

    readonly_fields = (
        "date_joined",
        "last_login",
        "avatar_preview",
        "last_login_display",
        "date_joined_display",
    )

    # Inline showing recent activity for this specific user
    # We attach the parent instance so the inline can filter by it
    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        inline = RecentAuditLogInline(self.model, self.admin_site)
        inline._parent_instance = obj
        return [inline]

    fieldsets = (
        # ── Section 1: Account credentials ──────────────────────────
        ("Account Credentials", {
            "fields": ("username", "password"),
            "description": (
                "The password field is hashed — use the "
                '<a href="password/">change password form</a> to update it.'
            ),
        }),
        # ── Section 2: Personal information ─────────────────────────
        ("Personal Information", {
            "fields": (
                ("first_name", "last_name"),
                "email",
                "phone_number",
            ),
        }),
        # ── Section 3: Staff profile ─────────────────────────────────
        ("Staff Profile", {
            "fields": ("avatar", "avatar_preview"),
            "classes": ("collapse",),
            "description": "Optional profile picture for Admin display.",
        }),
        # ── Section 4: Permissions & roles ──────────────────────────
        ("Permissions & Roles", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
            "description": (
                "Assign roles via <strong>Groups</strong>. Available roles: "
                "<em>Manager</em>, <em>Inventory Staff</em>, <em>Sales Staff</em>. "
                "Super Admin = is_superuser checkbox."
            ),
        }),
        # ── Section 5: Important dates (read-only) ───────────────────
        ("Important Dates", {
            "fields": ("date_joined", "last_login"),
            "classes": ("collapse",),
        }),
    )

    # Fields shown when CREATING a new user
    add_fieldsets = (
        ("Create New User", {
            "classes": ("wide",),
            "fields": (
                "username",
                ("first_name", "last_name"),
                "email",
                "phone_number",
                "password1",
                "password2",
                ("is_staff", "is_active"),
                "groups",
            ),
        }),
    )

    # ------------------------------------------------------------------
    # Custom list_display callables
    # ------------------------------------------------------------------

    @admin.display(description="")
    def avatar_thumbnail(self, obj):
        """Small circular avatar thumbnail in the list view."""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width:32px; height:32px; border-radius:50%; '
                'object-fit:cover; border:2px solid #dee2e6;" alt="Avatar" />',
                obj.avatar.url,
            )
        # Fallback: initials circle
        initials = (
            (obj.first_name[:1] + obj.last_name[:1]).upper()
            if (obj.first_name or obj.last_name)
            else obj.username[:2].upper()
        )
        return format_html(
            '<div style="width:32px; height:32px; border-radius:50%; '
            'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
            'display:flex; align-items:center; justify-content:center; '
            'color:white; font-size:12px; font-weight:700;">{}</div>',
            initials,
        )

    @admin.display(description="Full Name", ordering="first_name")
    def full_name(self, obj):
        return obj.get_full_name()

    @admin.display(description="Role")
    def role_badge(self, obj):
        """Visual role badge based on Django permissions/groups."""
        if obj.is_superuser:
            return mark_safe(
                '<span style="background:#6f42c1; color:white; padding:2px 8px; '
                'border-radius:10px; font-size:11px; font-weight:600;">👑 Super Admin</span>'
            )
        if obj.is_staff:
            groups = list(obj.groups.values_list("name", flat=True))
            if groups:
                group_name = groups[0]
                colour_map = {
                    "Manager":          "#fd7e14",
                    "Inventory Staff":  "#20c997",
                    "Sales Staff":      "#0dcaf0",
                }
                colour = colour_map.get(group_name, "#6c757d")
                return format_html(
                    '<span style="background:{}; color:white; padding:2px 8px; '
                    'border-radius:10px; font-size:11px; font-weight:600;">⚙️ {}</span>',
                    colour,
                    group_name,
                )
            return mark_safe(
                '<span style="background:#0d6efd; color:white; padding:2px 8px; '
                'border-radius:10px; font-size:11px; font-weight:600;">🛠 Staff</span>'
            )
        return mark_safe(
            '<span style="background:#e9ecef; color:#495057; padding:2px 8px; '
            'border-radius:10px; font-size:11px;">👤 Customer</span>'
        )

    @admin.display(description="Active", boolean=False, ordering="is_active")
    def is_active_badge(self, obj):
        if obj.is_active:
            return mark_safe(
                '<span style="color:#28a745; font-size:16px;" title="Active">●</span>'
            )
        return mark_safe(
            '<span style="color:#dc3545; font-size:16px;" title="Inactive">●</span>'
        )

    @admin.display(description="Date Joined", ordering="date_joined")
    def date_joined_display(self, obj):
        if obj.date_joined:
            return obj.date_joined.strftime("%d %b %Y")
        return "—"

    @admin.display(description="Last Login", ordering="last_login")
    def last_login_display(self, obj):
        if obj.last_login:
            return obj.last_login.strftime("%d %b %Y %H:%M")
        return mark_safe('<span style="color:#adb5bd;">Never</span>')

    @admin.display(description="Avatar Preview")
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width:80px; height:80px; border-radius:50%; '
                'object-fit:cover; border:3px solid #dee2e6;" alt="Avatar preview" />',
                obj.avatar.url,
            )
        return "No avatar uploaded."

    # ------------------------------------------------------------------
    # Security: prevent non-superusers from editing superusers
    # ------------------------------------------------------------------

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Staff who are not superusers can only see non-superuser accounts
        return qs.filter(is_superuser=False)

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting your own account or another superuser's account."""
        if obj is not None:
            if obj.pk == request.user.pk:
                return False
            if obj.is_superuser and not request.user.is_superuser:
                return False
        return super().has_delete_permission(request, obj)