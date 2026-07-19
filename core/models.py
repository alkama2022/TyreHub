from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model for TyreHub.

    Extends Django's AbstractUser to add:
    - Unique email (required for Djoser/JWT auth)
    - Optional phone number for staff contact
    - Optional avatar for admin profile display
    """

    email = models.EmailField(unique=True)

    # Staff profile fields — optional, used in Django Admin display
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Staff contact phone number",
    )
    avatar = models.ImageField(
        upload_to="staff/avatars/",
        blank=True,
        null=True,
        help_text="Staff profile picture",
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username

    def __str__(self):
        return self.get_full_name()