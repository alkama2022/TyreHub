import csv
from django.contrib import admin
from django.db.models import Count, Prefetch
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    Brand,
    ProductCategory,
    Product,
    ProductImage,
    OrderItem,
    Address,
    Review,
)

# ---------------------------------------------------------------------------
# Global Admin Actions
# ---------------------------------------------------------------------------

@admin.action(description="Mark selected items as Active")
def make_active(modeladmin, request, queryset):
    """Bulk action to mark objects as active."""
    queryset.update(is_active=True)
    modeladmin.message_user(request, "Selected items successfully marked as active.")


@admin.action(description="Mark selected items as Inactive")
def make_inactive(modeladmin, request, queryset):
    """Bulk action to mark objects as inactive."""
    queryset.update(is_active=False)
    modeladmin.message_user(request, "Selected items successfully marked as inactive.")


@admin.action(description="Export selected to CSV")
def export_to_csv(modeladmin, request, queryset):
    """Generic bulk action to export selected records to CSV format."""
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta.model_name}_export.csv'
    writer = csv.writer(response)
    
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    
    return response


# ---------------------------------------------------------------------------
# Inlines
# ---------------------------------------------------------------------------

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "thumbnail", "is_primary")
    readonly_fields = ("thumbnail",)

    @admin.display(description="Thumbnail preview")
    def thumbnail(self, obj):
        """Displays a secure thumbnail preview in the inline form."""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; border-radius: 4px;" alt="Product image preview" />',
                obj.image.url
            )
        return "-"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "quantity", "unit_price")
    autocomplete_fields = ("product",)
    readonly_fields = ("unit_price",)


class AddressInline(admin.StackedInline):
    model = Address
    extra = 0
    can_delete = False


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ("name", "description", "date")
    readonly_fields = ("date",)


# ---------------------------------------------------------------------------
# Catalog Admin Models
# ---------------------------------------------------------------------------

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("logo_preview", "name", "tyre_count", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)
    list_per_page = 50

    def get_queryset(self, request):
        """Optimized queryset using annotate to prevent N+1 counting queries."""
        return super().get_queryset(request).annotate(
            _tyre_count=Count("tyres")
        )

    @admin.display(description="Total Products", ordering="_tyre_count")
    def tyre_count(self, obj):
        return obj._tyre_count
    
    @admin.display(description="Logo")
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="height:30px; border-radius:4px;" alt="{}" />',
                obj.logo.url,
                obj.name
            )
        return "-"


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "tyre_count", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = 50

    def get_queryset(self, request):
        """Optimized queryset using annotate to prevent N+1 counting queries."""
        return super().get_queryset(request).annotate(_tyre_count=Count("tyres"))

    @admin.display(description="Total Products", ordering="_tyre_count")
    def tyre_count(self, obj):
        return obj._tyre_count


class InventoryFilter(admin.SimpleListFilter):
    """Custom filter to query products based on inventory ranges."""
    title = "inventory status"
    parameter_name = "inventory_status"

    def lookups(self, request, model_admin):
        return [
            ("out", "Out of stock"),
            ("low", "Low stock (< 10)"),
            ("in", "In stock"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "out":
            return queryset.filter(inventory=0)
        if self.value() == "low":
            return queryset.filter(inventory__gt=0, inventory__lt=10)
        if self.value() == "in":
            return queryset.filter(inventory__gte=10)
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "primary_image",
        "model_name",
        "brand",
        "category",
        "tire_size",
        "price",
        "inventory_status",
        "is_active",
    )
    list_editable = ("price", "is_active")
    list_filter = ("is_active", "brand", "category", InventoryFilter)
    search_fields = ("model_name", "brand__name", "tire_size")
    autocomplete_fields = ("brand", "category")
    inlines = [ProductImageInline, ReviewInline]
    
    # Performance Optimizations
    list_select_related = ("brand", "category")  # Prevents N+1 queries on foreign keys
    show_full_result_count = False               # Critical for scalability (100k+ rows) prevents slow COUNT(*)
    list_per_page = 50
    
    actions = [make_active, make_inactive, export_to_csv]

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Basic info", {
            "fields": ("brand", "category", "model_name", "tire_size", "is_active")
        }),
        ("Specifications", {
            "fields": (
                ("load_index", "speed_rating"),
            )
        }),
        ("Pricing & stock", {
            "fields": ("price", "inventory")
        }),
        ("Details", {
            "fields": ("description",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Stock Status", ordering="inventory")
    def inventory_status(self, obj):
        """Returns a color-coded pill based on the product inventory levels."""
        if obj.inventory == 0:
            color = "#dc3545" # Red
            text = "Out of Stock"
        elif obj.inventory < 10:
            color = "#ffc107" # Yellow
            text = "Low Stock"
        else:
            color = "#28a745" # Green
            text = "In Stock"
            
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            f"{text} ({obj.inventory})"
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            Prefetch("images", queryset=ProductImage.objects.filter(is_primary=True), to_attr="_primary_image")
        )

    @admin.display(description="Image & Actions")
    def primary_image(self, obj):
        edit_url = reverse("admin:catalog_product_change", args=[obj.id])
        add_url = reverse("admin:catalog_productimage_add") + f"?product={obj.id}"
        
        actions_html = format_html(
            '<div style="margin-top: 4px;">'
            '<a href="{}" style="font-size: 11px; padding: 2px 4px; background: #f0f0f0; border-radius: 3px; text-decoration: none; margin-right: 4px; color: #333;" title="Edit Product Images">✎ Edit</a>'
            '<a href="{}" style="font-size: 11px; padding: 2px 4px; background: #d4edda; border-radius: 3px; text-decoration: none; color: #155724;" title="Add New Image">➕ Add</a>'
            '</div>',
            edit_url,
            add_url
        )

        if hasattr(obj, "_primary_image") and obj._primary_image:
            img = obj._primary_image[0]
            if img.image:
                img_html = format_html(
                    '<a href="{}"><img src="{}" style="height: 40px; border-radius: 4px;" alt="Primary" /></a>',
                    edit_url,
                    img.image.url
                )
                return mark_safe(img_html + actions_html)
        
        no_img = mark_safe('<span style="color: #999; font-size: 11px; display: block; margin-bottom: 4px;">No Image</span>')
        return mark_safe(no_img + actions_html)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("thumbnail_preview", "product", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("product__model_name", "product__brand__name")
    autocomplete_fields = ("product",)
    
    # Performance Optimizations
    list_select_related = ("product", "product__brand")
    list_per_page = 50
    show_full_result_count = False

    @admin.display(description="Image Preview")
    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height: 40px; border-radius: 4px;" alt="Product preview" />',
                obj.image.url
            )
        return "-"


# ---------------------------------------------------------------------------
# Order & Utilities Admin
# ---------------------------------------------------------------------------

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "unit_price", "total_price")
    raw_id_fields = ("order",)
    autocomplete_fields = ("product",)
    
    # Performance Optimizations
    list_select_related = ("order", "product", "product__brand")
    list_per_page = 50
    show_full_result_count = False

    @admin.display(description="Total Price")
    def total_price(self, obj):
        total = obj.quantity * obj.unit_price
        return f"₦{total:,.2f}"


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("customer", "street", "city")
    search_fields = ("street", "city", "customer__user__first_name", "customer__user__last_name")
    raw_id_fields = ("customer",)
    
    # Performance Optimizations
    list_select_related = ("customer", "customer__user")
    list_per_page = 50


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "date_formatted")
    list_filter = ("date",)
    search_fields = ("name", "description", "product__model_name", "product__brand__name")
    autocomplete_fields = ("product",)
    
    # Performance Optimizations
    list_select_related = ("product", "product__brand")
    list_per_page = 50
    show_full_result_count = False

    @admin.display(description="Date Reviewed", ordering="date")
    def date_formatted(self, obj):
        return obj.date.strftime("%Y-%m-%d %H:%M")