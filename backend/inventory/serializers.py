from rest_framework import serializers
from .models import Product, Category, PantryItem, StorageLocation


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'barcode',
            'brand',
            'category'
        ]

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name']

class PantryItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = PantryItem
        fields = [
            'id',
            'household',
            'product',
            'quantity',
            'expiration_date',
            'storage_location',
            'added_at'
        ]

        read_only_fields = [
            'id',
            'added_at'
        ]
    def validate(self, attrs):
        household = attrs.get(
            'household',
            getattr(self.instance, 'household', None)
        )

        storage_location = attrs.get(
            'storage_location',
            getattr(self.instance, 'storage_location', None)
        )

        if (
            household is not None
            and storage_location is not None
            and storage_location.household_id != household.id
        ):
            raise serializers.ValidationError({
                'storage_location':
                    'Miejsce przechowywania musi należeć '
                    'do wskazanego gospodarstwa.'
            })

        return attrs

class StorageLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = StorageLocation
        fields = [
            'id',
            'household',
            'name'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        if self.instance is not None:
            household = attrs.get('household')

            if (
                    household is not None
                    and household.id != self.instance.household_id
            ):
                raise serializers.ValidationError({
                    'household': 'Nie można zmienić gospodarstwa '
                                 'istniejącego miejsca przechowywania.'
                })

        return attrs