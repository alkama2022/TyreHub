from django.conf import settings
from django.db import models
from django.utils import timezone

class AuditLog(models.Model):
    """
    Tracks all significant user actions across the TyreHub system.

    Records who did what and when, providing a full audit trail for:
    - Login / logout events
    - Password changes
    - Product / Order modifications
    - Any custom business-critical actions

    Entries are WRITE-ONLY by design — no update/delete allowed via Admin.
    """

    # Action category choices
    ACTION_LOGIN = "LOGIN"
    ACTION_LOGOUT = "LOGOUT"
    ACTION_LOGIN_FAILED = "LOGIN_FAILED"
    ACTION_PASSWORD_CHANGE = "PASSWORD_CHANGE"
    ACTION_CREATE = "CREATE"
    ACTION_UPDATE = "UPDATE"
    ACTION_DELETE = "DELETE"
    ACTION_DEACTIVATE = "DEACTIVATE"
    ACTION_ACTIVATE = "ACTIVATE"
    ACTION_OTHER = "OTHER"

    ACTION_CHOICES = [
        (ACTION_LOGIN, "Login"),
        (ACTION_LOGOUT, "Logout"),
        (ACTION_LOGIN_FAILED, "Failed Login"),
        (ACTION_PASSWORD_CHANGE, "Password Change"),
        (ACTION_CREATE, "Create"),
        (ACTION_UPDATE, "Update"),
        (ACTION_DELETE, "Delete"),
        (ACTION_DEACTIVATE, "Deactivate"),
        (ACTION_ACTIVATE, "Activate"),
        (ACTION_OTHER, "Other"),
    ]

    # The user who performed the action (nullable for anonymous/system actions)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="Performed by",
    )
    actor_username = models.CharField(
        max_length=150,
        blank=True,
        help_text="Snapshot of username at time of action (preserved even if user deleted)",
    )

    # What happened
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        default=ACTION_OTHER,
        db_index=True,
    )
    description = models.TextField(
        help_text="Human-readable description of the action",
    )

    # What was affected
    target_model = models.CharField(
        max_length=100,
        blank=True,
        help_text="The model/table that was affected (e.g. 'Product', 'Order')",
    )
    target_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Primary key of the affected record",
    )

    # Optional before/after data snapshot
    extra_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Optional JSON snapshot of before/after values",
    )

    # Request metadata
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the request",
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["actor", "-timestamp"]),
            models.Index(fields=["action", "-timestamp"]),
            models.Index(fields=["target_model", "target_id"]),
        ]

    def save(self, *args, **kwargs):
        # Snapshot the username so audit trail is preserved if user is deleted
        if self.actor and not self.actor_username:
            self.actor_username = self.actor.get_username()
        super().save(*args, **kwargs)

    def __str__(self):
        actor = self.actor_username or "Anonymous"
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {actor} — {self.get_action_display()}: {self.description[:60]}"
    def __str__(self):
        actor = self.actor_username or "Anonymous"
        local_time = timezone.localtime(self.timestamp)
        return (
        f"[{local_time:%Y-%m-%d %H:%M}] "
        f"{actor} — {self.get_action_display()}: {self.description[:60]}"
    )

# ---------------------------------------------------------------------------
# Utility function — log actions from anywhere in the codebase
# ---------------------------------------------------------------------------

def create_audit_log(
    *,
    actor=None,
    action=AuditLog.ACTION_OTHER,
    description="",
    target_model="",
    target_id="",
    extra_data=None,
    ip_address=None,
):
    """
    Convenience function to create an AuditLog entry.

    Usage:
        from accounts.models import create_audit_log, AuditLog

        create_audit_log(
            actor=request.user,
            action=AuditLog.ACTION_UPDATE,
            description="Updated product price",
            target_model="Product",
            target_id=str(product.id),
            ip_address=request.META.get("REMOTE_ADDR"),
        )
    """
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        description=description,
        target_model=target_model,
        target_id=str(target_id) if target_id else "",
        extra_data=extra_data,
        ip_address=ip_address,
    )
