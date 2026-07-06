from django.db.models import Count

from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin,DestroyModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter


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
    search_fields = ['model_name','description','brand__name','category__name','width']
    ordering_fields = ['price', 'model_name']

    def get_serializer_context(self):
        return {'request' : self.request}
    
    serializer_class = serializers.ProductSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = CustomPageNumberPagination
    search_fields = ['model_name','description','brand__name','category__name','width']
    ordering_fields = ['price', 'model_name']

    def get_serializer_context(self):
        return {'request' : self.request}
    
    def destroy(self, request, *args, **kwargs):
        if models.OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({"Error" : "Product Cannot be deleted becouse it is associated order items"})
        return super().destroy(request, *args, **kwargs)
    
class ProductCategoryViewSet(ModelViewSet):
    permission_classes = [permissions.IsAdminOrReadOnly]
    queryset = models.ProductCategory.objects.annotate(products_count=Count('tyres')).all()
    serializer_class = serializers.ProductCategorySerializer
    
    def get_serializer_context(self):
        return {'request' : self.request}
    
    def destroy(self, request, *args, **kwargs):
        if models.Product.objects.filter(category_id=kwargs['pk']).count() > 0:
            return Response({"Error" : "Category Cannot be deleted becouse it is associated with products"})
        return super().destroy(request, *args, **kwargs)
    
    
class ReviewViewSet(ModelViewSet):
    def get_queryset(self):
        return models.Review.objects.filter(product_id=self.kwargs['product_pk'])
    serializer_class = serializers.ReviewSerializer
    
    def get_serializer_context(self):
        return {'product' : self.kwargs['product_pk']}



class BrandViewSet(ModelViewSet):
    permission_classes = [permissions.IsAdminOrReadOnly]
    pagination_class = CustomPageNumberPagination
    queryset = models.Brand.objects.prefetch_related('tyres').annotate(products_count=Count('tyres')).all()
    serializer_class = serializers.BrandSerializer
    
    

class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin,  GenericViewSet):
    queryset = models.Cart.objects.prefetch_related('items__product').all()
    serializer_class = serializers.CartSerializer
    
class CartItemViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','delete']
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return serializers.UpdateCartItemSerializer
        return serializers.CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id' : self.kwargs['cart_pk']}
    
    def get_queryset(self):
        return models.CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')

class ProductImageViewSet(ModelViewSet):
    def get_queryset(self):
        return models.ProductImage.objects.filter(product_id=self.kwargs['product_pk'])
   
    serializer_class = serializers.ProductImageSerializer
    
    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}



from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny,IsAdminUser

class SentCartMessageViewSet(ModelViewSet):
    queryset = models.SentCartMessage.objects.all()
    serializer_class = serializers.SentCartMessageSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]