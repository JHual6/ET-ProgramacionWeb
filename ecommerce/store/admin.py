from django.contrib import admin
from .models import Product

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'stock', 'created_at', 'image')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
