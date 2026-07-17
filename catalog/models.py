from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.core.validators import MinValueValidator,MinLengthValidator
from uuid import uuid4
# Create your models here.


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to="store/brands", blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.name)
            unique_slug = slug
            counter = 1

            while Brand.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{slug}-{counter}"
                counter += 1

            self.slug = unique_slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]     

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
    tire_size = models.CharField(max_length=17)

    load_index = models.PositiveIntegerField()
    speed_rating = models.CharField(max_length=2)  # H, V

    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    description = models.TextField(blank=True)
    inventory = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # class Meta:
    #     indexes = [
    #             models.Index(fields=["tire_size"]),
    #             models.Index(fields=["is_active"]),
    #             models.Index(fields=["price"]),
    #             models.Index(fields=["created_at"]),
    #              ]
        
    #     constraints = [
    #             models.UniqueConstraint(
    #                    fields=["brand", "model_name", "tire_size"],
    #                    name="unique_product"
    #                                   )
    #                   ]
        #   ordering = ["-created_at"]
    class Meta:
        unique_together = ("brand", "model_name","tire_size")

    # def __str__(self):
    #     return f"{self.brand.name} {self.model_name} {self.width}/{self.aspect_ratio}R{self.rim_diameter}"

    # def clean(self):
    #     """Business rule validation"""
    #     if self.discount_price and self.discount_price > self.price:
    #         raise ValueError("Discount price cannot be greater than price")

class ProductImage(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="images")
    image = models.ImageField(upload_to="store/images", blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    def __str__(self):
        return f"Image of {self.product.model_name}"
    
    # class Meta:
    #     ordering = ["-is_primary", "id"]


        
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
    
    class Meta:
        indexes = [
               models.Index(fields=["order"]),
               models.Index(fields=["product"]),
                  ]
  
  
class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE,primary_key=True)
    # customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    # is_default = models.BooleanField(default=False)

class Cart(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    
    
    class Meta:
        # constraints = [
        #           models.UniqueConstraint(
        #                        fields=["cart", "product"],
        #                        name="unique_cart_product"
        #                                  )
        #              ]
        unique_together =[['cart','product']]

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    # rating = models.PositiveSmallIntegerField()
    

class SentCartMessage(models.Model):
    session_key = models.CharField(max_length=255,null=True,blank=True)
    contact_name = models.CharField(max_length=255,blank=True)
    contact_phone = models.CharField(max_length=15,blank=True)
    contact_email = models.EmailField(blank=True)
    contact_note = models.TextField(blank=True)
    
    #snapshot of cart at the time of sending
    
    items_snapshot = models.JSONField(help_text="List of {product_name, quantity , parice} at sending time")
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    message_text = models.TextField(help_text="Exact message sent to the shop owner")
    whatsapp_url = models.URLField(
    max_length=2000,
    blank=True,
    help_text="Generate click-to-chat URL"
)
    sent_via = models.CharField(max_length=20,choices=[('whatsapp','WhatsApp'),('sms','SMS')],default='whatsapp')
    
    created_at = models.DateTimeField(auto_now_add=True)
    # created_at = models.DateTimeField(auto_now_add=True,db_index=True)
    ip_address = models.GenericIPAddressField(null=True,blank=True)
    
    def __str__(self):
        return f'Message {self.id} at {self.created_at}'
    