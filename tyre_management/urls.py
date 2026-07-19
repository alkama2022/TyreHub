from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('core.urls')),
    path("admin/", admin.site.urls),
    path("api/", include("catalog.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),

    # ── Password reset flow (Django built-in secure views) ─────────────────
    # Provides:
    #   /accounts/password_reset/          → Step 1: Enter email
    #   /accounts/password_reset/done/     → Step 2: Email sent confirmation
    #   /accounts/reset/<uidb64>/<token>/  → Step 3: Enter new password
    #   /accounts/reset/done/              → Step 4: Success page
    path("accounts/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += debug_toolbar_urls()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Serve media files in production (or delegate to nginx/S3 in real deployments)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)