from django.contrib import admin
from .models import (
    Brand, TyreCategory, Tyre, TyreImage,
    Customer, Order, OrderItem,
    Address, Cart, CartItem, Review
)

# =========================
# BRAND
# =========================
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


# =========================
# TYRE CATEGORY
# =========================
@admin.register(TyreCategory)
class TyreCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


# =========================
# TYRE IMAGE INLINE
# =========================
class TyreImageInline(admin.TabularInline):
    model = TyreImage
    extra = 1


# =========================
# TYRE
# =========================
@admin.register(Tyre)
class TyreAdmin(admin.ModelAdmin):
    list_display = (
        'brand', 'model_name', 'category',
        'width', 'aspect_ratio', 'rim_diameter',
        'price', 'discount_price', 'is_active', 'created_at'
    )
    
    list_filter = (
        'brand', 'category', 'is_active',
        'width', 'rim_diameter'
    )

    search_fields = ('model_name', 'brand__name')
    ordering = ('-created_at',)

    inlines = [TyreImageInline]

    list_editable = ('price', 'discount_price', 'is_active')


# =========================
# CUSTOMER
# =========================
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'phone_number', 'membership', 'birth_date'
    )

    list_filter = ('membership',)
    search_fields = ('user__first_name', 'user__last_name', 'phone_number')
    ordering = ('user__first_name',)


# =========================
# ADDRESS
# =========================
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street', 'city', 'country', 'customer')
    search_fields = ('street', 'city', 'customer__user__first_name')


# =========================
# ORDER ITEM INLINE
# =========================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


# =========================
# ORDER
# =========================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'payment_status', 'placed_at')
    list_filter = ('payment_status', 'placed_at')
    search_fields = ('customer__user__first_name',)
    inlines = [OrderItemInline]
    ordering = ('-placed_at',)


# =========================
# CART ITEM INLINE
# =========================
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


# =========================
# CART
# =========================
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    inlines = [CartItemInline]


# =========================
# REVIEW
# =========================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'date')
    search_fields = ('product__model_name', 'name')
    list_filter = ('date',)
    ordering = ('-date',)