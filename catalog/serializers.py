from rest_framework import serializers
from . import models


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['id','model_name','price']

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
    products_count = serializers.IntegerField(read_only = True)
    class Meta:
        model = models.ProductCategory
        fields = ['id','name','products_count']  
        
          
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ['id','name','description']
    
    def create(self, validated_data):
        product_id = self.context['product']
        review = models.Review.objects.create(product_id=product_id, **validated_data)
        return review
  

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        
        cart_item, created = models.CartItem.objects.get_or_create(cart_id=cart_id, product_id=product_id, defaults={'quantity': quantity})
        cart_item.quantity = quantity
        cart_item.save()
        return cart_item
        
    class Meta:
        model = models.CartItem
        fields = ['id','product_id','quantity']
        
    
  
class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(self, obj):
        return obj.product.price * obj.quantity
    
    class Meta:
        model = models.CartItem
        fields = ['id','product','quantity','total_price']
        
    
    

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())
    class Meta:
        model = models.Cart
        fields = ['id','items','total_price']
        
        

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ['quantity']







class OrderSerializer(serializers.ModelSerializer):
#   items = OrderItemSerialize(many=True)
  class Meta:
    model = models.Order
    fields = ['id','customer','placed_at','payment_status']
