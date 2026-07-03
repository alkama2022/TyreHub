from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.core.validators import MinValueValidator,MinLengthValidator
from uuid import uuid4
# Create your models here.


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(self.name)
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']        

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)  # SUV, Sedan, Truck, Motorcycle
    slug = models.SlugField(unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(self.name)
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    brand = models.ForeignKey(Brand,on_delete=models.PROTECT,related_name="tyres")
    category = models.ForeignKey(ProductCategory,on_delete=models.PROTECT,related_name="tyres")
    model_name = models.CharField(max_length=150)
    width = models.PositiveIntegerField()          # 205
    aspect_ratio = models.PositiveIntegerField()   # 55
    rim_diameter = models.PositiveIntegerField()   # 16

    load_index = models.PositiveIntegerField()
    speed_rating = models.CharField(max_length=2)  # H, V

    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    inventory = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["width", "aspect_ratio", "rim_diameter"]),
        ]
        unique_together = ("brand", "model_name", "width", "rim_diameter")

    def __str__(self):
        return f"{self.brand.name} {self.model_name} {self.width}/{self.aspect_ratio}R{self.rim_diameter}"

    def clean(self):
        """Business rule validation"""
        if self.discount_price and self.discount_price > self.price:
            raise ValueError("Discount price cannot be greater than price")

class ProductImage(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="images")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    def __str__(self):
        return f"Image of {self.product.model_name}"
      
from django.db import models


        
class Customer(models.Model):
    MEMBER_SHIP_BRONZE = 'B'
    MEMBER_SHIP_SILVER = 'S'
    MEMBER_SHIP_GOLD = 'G'
    MEMBER_SHIP_CHOICES = [
        (MEMBER_SHIP_BRONZE, 'Bronze'),
        (MEMBER_SHIP_SILVER, 'Silver'),
        (MEMBER_SHIP_GOLD, 'Gold'),
    ]
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    membership = models.CharField(max_length=1, choices=MEMBER_SHIP_CHOICES, default=MEMBER_SHIP_BRONZE)
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        permissions = [
            ('view_history', 'Can view history')
        ]

class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETED = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETED, 'Completed'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
    ]
    
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    
    # class Meta:
    #     permissions = [
    #         ('cancel_order', 'Can cancel order')
    #     ]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='orderitems')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
  
  
class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE,primary_key=True)

class Cart(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    
    class Meta:
        unique_together =[['cart','product']]

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)