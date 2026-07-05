from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )

    list_filter = ("is_staff", "is_active", "is_superuser")

    search_fields = ("username", "email", "first_name", "last_name")

    ordering = ("id",)

    # ❌ REMOVE EMAIL FROM FIELDSETS EXTENSION
    fieldsets = UserAdmin.fieldsets

    add_fieldsets = UserAdmin.add_fieldsets