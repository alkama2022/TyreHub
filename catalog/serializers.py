from rest_framework import serializers
from django.db.models import F, Sum
from . import models


class SimpleProductSerializer(serializers.ModelSerializer):
    brand = serializers.StringRelatedField(read_only=True)
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        images = list(obj.images.all())
        primary = next((img for img in images if img.is_primary), None) or (images[0] if images else None)
        if not primary or not primary.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(primary.image.url)
        return primary.image.url

    class Meta:
        model = models.Product
        fields = ['id', 'model_name', 'price', 'brand', 'tire_size', 'image']



# class SimpleProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.Product
#         fields = ['id','model_name','price']
        
# class SimpleProductSerializer(serializers.ModelSerializer):
#     brand = serializers.StringRelatedField(read_only=True)

#     class Meta:
#         model = models.Product
#         fields = ['id', 'model_name', 'price', 'brand', 'tire_size', 'images']


class ProductImageSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        product_id = self.context['product_id']
        return models.ProductImage.objects.create(product_id=product_id, **validated_data)
    
    class Meta:
        model = models.ProductImage
        fields = ['id','image','is_primary']



class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    brand = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)

    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Brand.objects.all(),
        source='brand',
        write_only=True
    )

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=models.ProductCategory.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = models.Product
        fields = [
            'id',
            'brand',
            'category',
            'brand_id',
            'category_id',
            'model_name',
            'tire_size',
            'load_index',
            'speed_rating',
            'price',
            'description',
            'inventory',
            'images',
        ]



# class ProductSerializer(serializers.ModelSerializer):
#     images = ProductImageSerializer(many=True, read_only=True)
#     brand = serializers.StringRelatedField(read_only=True)
#     category = serializers.StringRelatedField(read_only=True)

#     class Meta:
#         model = models.Product
#         fields = [
#             'id', 'brand', 'category',
#             'brand_id', 'category_id',
#             'model_name',  'tire_size',
#             'load_index', 'speed_rating', 'price', 'description',
#             'inventory', 'images',
#         ]


class BrandSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only = True)
    class Meta:
        model = models.Brand
        fields = ['id','name','products_count','logo']

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
        # CartItem.objects.filter(cart=cart).aggregate(
        #                        total=Sum(F("quantity") * F("product__price"))
        #                        )
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


class SentCartMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SentCartMessage
        fields = [
            'id',
            'contact_name',
            'contact_phone',
            'contact_email',
            'contact_note',
            'items_snapshot',
            'total_price',
            'message_text',
            'whatsapp_url',
            'sent_via',
            'created_at',
            'ip_address',
        ]
        #read_only_fields = fields   # all fields are read-only (no creation/update via API)