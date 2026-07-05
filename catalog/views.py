
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter



from django_filters.rest_framework import DjangoFilterBackend
from . import models
from . import serializers
from .filters import ProductFilter
from .pagination import CustomPageNumberPagination



class ProductViewSet(ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = CustomPageNumberPagination
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
    queryset = models.ProductCategory.objects.all()
    serializer_class = serializers.ProductCategorySerializer
    
    
class ReviewViewSet(ModelViewSet):
    def get_queryset(self):
        return models.Review.objects.filter(product_id=self.kwargs['product_pk'])
    serializer_class = serializers.ReviewSerializer
    
    def get_serializer_context(self):
        return {'product' : self.kwargs['product_pk']}



class BrandViewSet(ModelViewSet):
    queryset = models.Brand.objects.all()
    serializer_class = serializers.BrandSerializer
    
    
    