from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Brand,
    ProductCategory,
    Product,
    ProductImage,
    # Customer,
    # Order,
    OrderItem,
    Address,
    # Cart,
    # CartItem,
    Review,
)


# ---------------------------------------------------------------------------
# Inlines
# ---------------------------------------------------------------------------


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

    fields = ("image", "thumbnail", "is_primary")
    readonly_fields = ("thumbnail",)

    def thumbnail(self, obj):
        if obj.image:
            return format_html(
            f'<img src="{obj.image.url}" width="100" />',
            obj.image.url,
        )
        return "No image"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ["product", "quantity", "unit_price"]
    autocomplete_fields = ["product"]
    readonly_fields = ["unit_price"]


# class CartItemInline(admin.TabularInline):
#     model = CartItem
#     extra = 0
#     fields = ["product", "quantity"]
#     autocomplete_fields = ["product"]


class AddressInline(admin.StackedInline):
    model = Address
    extra = 0
    can_delete = False


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ["name", "description", "date"]
    readonly_fields = ["date"]


# ---------------------------------------------------------------------------
# Catalog admin
# ---------------------------------------------------------------------------

from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from .models import Brand


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "tyre_count", "created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["name"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            tyre_count=Count("tyres")  # ⚠️ confirm related_name
        )

    @admin.display(description="Products")
    def tyre_count(self, obj):
        return obj.tyre_count
    
    @admin.display(description="Logo")
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="height:30px; border-radius:4px;" />',
                obj.logo.url
            )
        return "-"


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "tyre_count", "created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_tyre_count=Count("tyres"))

    @admin.display(description="Products")
    def tyre_count(self, obj):
        return obj._tyre_count


class InventoryFilter(admin.SimpleListFilter):
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
    list_display = [
        "__str__",
        "brand",
        "category",
        "size",
        "price",
        "inventory",
        "is_active",
    ]
    list_editable = ["price", "is_active"]
    list_filter = ["is_active", "brand", "category", InventoryFilter]
    search_fields = ["model_name", "brand__name"]
    autocomplete_fields = ["brand", "category"]
    inlines = [ProductImageInline, ReviewInline]
    list_select_related = ["brand", "category"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Basic info", {
            "fields": ("brand", "category", "model_name","tire_size", "is_active")
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

    @admin.display(description="Size")
    def size(self, obj):
        return obj.tire_size


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["product", "is_primary"]
    list_filter = ["is_primary"]
    autocomplete_fields = ["product"]


# ---------------------------------------------------------------------------
# Customer / order admin
# ---------------------------------------------------------------------------

# @admin.register(Customer)
# class CustomerAdmin(admin.ModelAdmin):
#     list_display = ["__str__", "membership", "phone_number", "birth_date"]
#     list_filter = ["membership"]
#     search_fields = ["user__first_name", "user__last_name", "user__email", "phone_number"]
#     autocomplete_fields = ["user"]
#     inlines = [AddressInline]


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ["id", "customer", "payment_status", "placed_at", "item_count", "order_total"]
#     list_filter = ["payment_status", "placed_at"]
#     search_fields = ["customer__user__first_name", "customer__user__last_name"]
#     autocomplete_fields = ["customer"]
#     inlines = [OrderItemInline]
#     date_hierarchy = "placed_at"

#     def get_queryset(self, request):
#         return super().get_queryset(request).prefetch_related("items")

#     @admin.display(description="Items")
#     def item_count(self, obj):
#         return obj.items.count()

#     @admin.display(description="Total")
#     def order_total(self, obj):
#         total = sum(item.quantity * item.unit_price for item in obj.items.all())
#         return f"₦{total:,.2f}"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "quantity", "unit_price"]
    autocomplete_fields = ["order", "product"]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["customer", "street", "city"]
    search_fields = ["street", "city", "customer__user__first_name"]
    autocomplete_fields = ["customer"]


# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ["id", "created_at", "item_count"]
#     inlines = [CartItemInline]
#     search_fields = ["id"]

#     @admin.display(description="Items")
#     def item_count(self, obj):
#         return obj.items.count()


# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = ["cart", "product", "quantity"]
#     autocomplete_fields = ["cart", "product"]
    


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["product", "name", "date"]
    list_filter = ["date"]
    search_fields = ["name", "description", "product__model_name"]
    autocomplete_fields = ["product"]