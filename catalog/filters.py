from django_filters.rest_framework import FilterSet

from catalog.models import Product


class ProductFilter(FilterSet):
  class Meta:
    model = Product
    fields = {
      'category': ['exact'],
      'brand': ['exact'],
      'price': ['exact', 'gte', 'lte']
    }