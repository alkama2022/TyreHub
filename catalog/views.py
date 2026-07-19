from django.db.models import Count

from rest_framework import status
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin,DestroyModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.permissions import AllowAny,IsAdminUser

from django_filters.rest_framework import DjangoFilterBackend
from . import models
from . import serializers
from . import permissions
from .filters import ProductFilter
from .pagination import CustomPageNumberPagination


class ProductViewSet(ModelViewSet):
    queryset = models.Product.objects.prefetch_related('images').select_related('category','brand').all()
    serializer_class = serializers.ProductSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = CustomPageNumberPagination
    permission_classes = [permissions.IsAdminOrReadOnly]
    search_fields = ['model_name','description','brand__name','category__name']
    ordering_fields = ['price', 'model_name']

    def get_serializer_context(self):
        return {'request' : self.request}
    
    
    def destroy(self, request, *args, **kwargs):
        if models.OrderItem.objects.filter(product_id=kwargs['pk']).exists():
            return Response(
                {"detail": "Product cannot be deleted because it is associated with existing order items."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
    
    
    
class ProductCategoryViewSet(ModelViewSet):
    permission_classes = [permissions.IsAdminOrReadOnly]
    queryset = models.ProductCategory.objects.annotate(products_count=Count('tyres')).all()
    serializer_class = serializers.ProductCategorySerializer
    pagination_class = CustomPageNumberPagination

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_serializer_context(self):
        return {'request' : self.request}
    
    def destroy(self, request, *args, **kwargs):
        if models.Product.objects.filter(category_id=kwargs['pk']).exists():
            return Response(
                {"detail": "Category cannot be deleted because it is associated with existing products."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
    
    
class ReviewViewSet(ModelViewSet):
    pagination_class = CustomPageNumberPagination
    def get_queryset(self):
        return models.Review.objects.filter(product_id=self.kwargs['product_pk']).order_by("-date")
    serializer_class = serializers.ReviewSerializer
    
    def get_serializer_context(self):
        return {'product' : self.kwargs['product_pk']}



class BrandViewSet(ModelViewSet):
    permission_classes = [permissions.IsAdminOrReadOnly]
    pagination_class = CustomPageNumberPagination
    queryset = models.Brand.objects.annotate(products_count=Count('tyres')).all()
    serializer_class = serializers.BrandSerializer
    
    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    

class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin,  GenericViewSet):
    # from django.db.models import Prefetch
    # queryset = models.Cart.objects.prefetch_related(
           # Prefetch(
               # "items",
               # queryset=models.CartItem.objects.select_related(
                             # "product"
                             # )
                  # )
                  # )
    queryset = models.Cart.objects.prefetch_related(
        'items__product__brand',
        'items__product__images'
    ).all()
    serializer_class = serializers.CartSerializer
    
class CartItemViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','delete']
    pagination_class = CustomPageNumberPagination
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return serializers.UpdateCartItemSerializer
        return serializers.CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id' : self.kwargs['cart_pk']}
    
    def get_queryset(self):
        return models.CartItem.objects.filter(
            cart_id=self.kwargs['cart_pk']
        ).select_related(
            'product__brand'
        ).prefetch_related(
            'product__images'
        )

class ProductImageViewSet(ModelViewSet):
    pagination_class = CustomPageNumberPagination
    def get_queryset(self):
        return models.ProductImage.objects.filter(product_id=self.kwargs['product_pk']).order_by(
                                                                                                "-is_primary",
                                                                                                 "id"
                                                                                                  )
   
    serializer_class = serializers.ProductImageSerializer
    
    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}





class SentCartMessageViewSet(ModelViewSet):
    queryset = models.SentCartMessage.objects.all()
    serializer_class = serializers.SentCartMessageSerializer
    pagination_class = CustomPageNumberPagination

    def get_permissions(self):
        if self.request.method == "POST":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]