from rest_framework import serializers
from . import models


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['id','brand','category','model_name','width','aspect_ratio','rim_diameter','load_index','speed_rating','price','description','inventory']
    
    brand = serializers.StringRelatedField()
    category = serializers.StringRelatedField()

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Brand
        fields = ['id','name']

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductCategory
        fields = ['id','name']  
        
          
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ['id','name','description']
    
    def create(self, validated_data):
        product_id = self.context['product']
        review = models.Review.objects.create(product_id=product_id, **validated_data)
        return review