from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Accounts & Audit"

    def ready(self):
        """
        Import signals when the app is fully loaded.
        This ensures signals are registered exactly once at startup.
        """
        import accounts.signals  # noqa: F401
