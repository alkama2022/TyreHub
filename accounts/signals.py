"""
Audit logging signals for TyreHub.

Automatically logs:
- Successful user logins
- Failed login attempts
- User logouts
- Password changes (detected via pre_save on User model)

These signals connect in AccountsConfig.ready() so they activate only once.
"""

from django.contrib.auth import user_logged_in, user_logged_out, user_login_failed
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import AuditLog, create_audit_log


def _get_ip(request):
    """Extract the real client IP, handling reverse-proxy X-Forwarded-For."""
    if request is None:
        return None
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


# ---------------------------------------------------------------------------
# Authentication signals
# ---------------------------------------------------------------------------

@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    """Log every successful login."""
    create_audit_log(
        actor=user,
        action=AuditLog.ACTION_LOGIN,
        description=f"User '{user.get_username()}' logged in successfully.",
        ip_address=_get_ip(request),
    )


@receiver(user_login_failed)
def on_user_login_failed(sender, credentials, request, **kwargs):
    """Log every failed login attempt (without exposing the attempted password)."""
    attempted_username = credentials.get("username", "unknown")
    create_audit_log(
        actor=None,
        action=AuditLog.ACTION_LOGIN_FAILED,
        description=f"Failed login attempt for username: '{attempted_username}'.",
        ip_address=_get_ip(request),
    )


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    """Log every logout event."""
    if user:
        create_audit_log(
            actor=user,
            action=AuditLog.ACTION_LOGOUT,
            description=f"User '{user.get_username()}' logged out.",
            ip_address=_get_ip(request),
        )


# ---------------------------------------------------------------------------
# Password change detection
# ---------------------------------------------------------------------------

@receiver(pre_save, sender=get_user_model())
def on_user_pre_save(sender, instance, **kwargs):
    """
    Detect and log password changes.

    Compares the incoming hashed password against the stored one.
    Only fires when an existing user (pk already set) changes their password.
    Never logs or stores plain-text passwords.
    """
    if not instance.pk:
        # Brand new user — not a password change
        return

    try:
        previous = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    if previous.password != instance.password:
        create_audit_log(
            actor=instance,
            action=AuditLog.ACTION_PASSWORD_CHANGE,
            description=f"Password was changed for user '{instance.get_username()}'.",
            target_model="User",
            target_id=str(instance.pk),
        )
