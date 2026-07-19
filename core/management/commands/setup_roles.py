"""
Management command: setup_roles

Creates the three standard TyreHub staff roles as Django Groups and assigns
the appropriate model permissions to each.

This command is IDEMPOTENT — safe to run multiple times.
Running it again will update permissions without duplicating anything.

Usage:
    python manage.py setup_roles

Roles created:
    Manager         — Full catalog management + customer/order oversight
    Inventory Staff — Product and stock management only
    Sales Staff     — Order management and customer view only
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


# ---------------------------------------------------------------------------
# Role definitions
# ---------------------------------------------------------------------------
# Each entry maps a group name to a list of (app_label, model, codename) tuples.
# codename format: add_<model> | change_<model> | delete_<model> | view_<model>

ROLE_PERMISSIONS = {
    "Manager": [
        # Products
        ("catalog", "product",         "view_product"),
        ("catalog", "product",         "add_product"),
        ("catalog", "product",         "change_product"),
        ("catalog", "product",         "delete_product"),
        # Product images
        ("catalog", "productimage",    "view_productimage"),
        ("catalog", "productimage",    "add_productimage"),
        ("catalog", "productimage",    "change_productimage"),
        ("catalog", "productimage",    "delete_productimage"),
        # Brands
        ("catalog", "brand",           "view_brand"),
        ("catalog", "brand",           "add_brand"),
        ("catalog", "brand",           "change_brand"),
        # Categories
        ("catalog", "productcategory", "view_productcategory"),
        ("catalog", "productcategory", "add_productcategory"),
        ("catalog", "productcategory", "change_productcategory"),
        # Orders
        ("catalog", "order",           "view_order"),
        ("catalog", "order",           "add_order"),
        ("catalog", "order",           "change_order"),
        ("catalog", "orderitem",       "view_orderitem"),
        ("catalog", "orderitem",       "add_orderitem"),
        ("catalog", "orderitem",       "change_orderitem"),
        # Customers
        ("catalog", "customer",        "view_customer"),
        ("catalog", "customer",        "change_customer"),
        ("catalog", "address",         "view_address"),
        ("catalog", "address",         "change_address"),
        # Reviews
        ("catalog", "review",          "view_review"),
        ("catalog", "review",          "delete_review"),
        # Audit logs — managers can view
        ("accounts", "auditlog",       "view_auditlog"),
    ],

    "Inventory Staff": [
        # Products — full management
        ("catalog", "product",         "view_product"),
        ("catalog", "product",         "add_product"),
        ("catalog", "product",         "change_product"),
        # Product images
        ("catalog", "productimage",    "view_productimage"),
        ("catalog", "productimage",    "add_productimage"),
        ("catalog", "productimage",    "change_productimage"),
        ("catalog", "productimage",    "delete_productimage"),
        # Brands — view + add + change (no delete)
        ("catalog", "brand",           "view_brand"),
        ("catalog", "brand",           "add_brand"),
        ("catalog", "brand",           "change_brand"),
        # Categories — view only
        ("catalog", "productcategory", "view_productcategory"),
        ("catalog", "productcategory", "add_productcategory"),
        ("catalog", "productcategory", "change_productcategory"),
        # Orders — view only (to know what was ordered)
        ("catalog", "order",           "view_order"),
        ("catalog", "orderitem",       "view_orderitem"),
    ],

    "Sales Staff": [
        # Products — view only (to answer customer queries)
        ("catalog", "product",         "view_product"),
        ("catalog", "productimage",    "view_productimage"),
        ("catalog", "brand",           "view_brand"),
        ("catalog", "productcategory", "view_productcategory"),
        # Orders — create and manage
        ("catalog", "order",           "view_order"),
        ("catalog", "order",           "add_order"),
        ("catalog", "order",           "change_order"),
        ("catalog", "orderitem",       "view_orderitem"),
        ("catalog", "orderitem",       "add_orderitem"),
        ("catalog", "orderitem",       "change_orderitem"),
        # Customers — view only
        ("catalog", "customer",        "view_customer"),
        ("catalog", "address",         "view_address"),
        # Reviews — view only
        ("catalog", "review",          "view_review"),
    ],
}


class Command(BaseCommand):
    help = (
        "Sets up TyreHub staff roles as Django Groups with correct permissions. "
        "Safe to run multiple times (idempotent)."
    )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\n[*] Setting up TyreHub staff roles...\n"))

        for role_name, perms in ROLE_PERMISSIONS.items():
            group, created = Group.objects.get_or_create(name=role_name)
            status = self.style.SUCCESS("CREATED") if created else self.style.WARNING("EXISTS ")
            self.stdout.write(f"  Group '{role_name}': {status}")

            permission_objects = []
            missing = []

            for app_label, model_name, codename in perms:
                try:
                    ct = ContentType.objects.get(app_label=app_label, model=model_name)
                    perm = Permission.objects.get(content_type=ct, codename=codename)
                    permission_objects.append(perm)
                except (ContentType.DoesNotExist, Permission.DoesNotExist):
                    missing.append(f"{app_label}.{codename}")

            group.permissions.set(permission_objects)

            self.stdout.write(
                f"    [ok] Assigned {len(permission_objects)} permission(s)."
            )
            if missing:
                for m in missing:
                    self.stdout.write(
                        f"    {self.style.ERROR('[WARN] Not found')}: {m} "
                        f"(run migrations first)"
                    )

        self.stdout.write(
            self.style.SUCCESS(
                "\n[ok] Role setup complete!\n"
                "   Assign users to groups via:\n"
                "   Admin > Users > [User] > Permissions & Roles > Groups\n"
            )
        )

