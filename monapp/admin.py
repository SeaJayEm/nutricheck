from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'brands', 'nutriscore_score', 'ecoscore_score')
    search_fields = ('product_name', 'brands')
# Register your models here.
