from django.db import models
from django.utils.text import slugify

# Create your models here.


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']        

class TyreCategory(models.Model):
    name = models.CharField(max_length=100)  # SUV, Sedan, Truck, Motorcycle
    slug = models.SlugField(unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tyre(models.Model):
    brand = models.ForeignKey(Brand,on_delete=models.PROTECT,related_name="tyres")
    category = models.ForeignKey(TyreCategory,on_delete=models.PROTECT,related_name="tyres")
    model_name = models.CharField(max_length=150)
    width = models.PositiveIntegerField()          # 205
    aspect_ratio = models.PositiveIntegerField()   # 55
    rim_diameter = models.PositiveIntegerField()   # 16

    load_index = models.PositiveIntegerField()
    speed_rating = models.CharField(max_length=2)  # H, V

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    description = models.TextField(blank=True)
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

class TyreImage(models.Model):
    tyre = models.ForeignKey(Tyre,on_delete=models.CASCADE,related_name="images")
    image = models.ImageField(upload_to="tyres/")
    is_primary = models.BooleanField(default=False)
    def __str__(self):
        return f"Image of {self.tyre.model_name}"
      
from django.db import models


class Customer(models.Model):
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ['-created_at']