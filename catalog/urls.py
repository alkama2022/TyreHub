from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from . import views

# Top-level router
router = routers.DefaultRouter()

router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'productsCategories', views.ProductCategoryViewSet, basename='category')
router.register(r'productsBrand', views.BrandViewSet, basename='brand')
router.register(r'cart', views.CartViewSet, basename='cart')

# Nested routers
product_router = nested_routers.NestedDefaultRouter(
    router,
    r'products',
    lookup='product'
)

nested_cart_router = nested_routers.NestedDefaultRouter(
    router,
    r'cart',
    lookup='cart'
)



product_router.register(
    r'reviews',
    views.ReviewViewSet,
    basename='product-reviews'
)

nested_cart_router.register(
    r'items',
    views.CartItemViewSet,
    basename='cart-items'
)



urlpatterns = router.urls + product_router.urls + nested_cart_router.urls