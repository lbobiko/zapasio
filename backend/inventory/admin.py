from django.contrib import admin
from .models import Product, Category, StorageLocation, PantryItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'barcode')
    search_fields = ('name', 'brand', 'barcode')


@admin.register(StorageLocation)
class StorageLocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'household')
    list_filter = ('household',)


@admin.register(PantryItem)
class PantryItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'product',
        'household',
        'quantity',
        'expiration_date',
        'storage_location'
    )

    list_filter = (
        'household',
        'storage_location',
        'expiration_date'
    )

    search_fields = ('product__name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
