from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)

    barcode = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    brand = models.CharField(
        max_length=100,
        blank=True,
    )

    category = models.CharField(
        max_length=100,

    )

    def __str__(self):
        return self.name


class StorageLocation(models.Model):
    household = models.ForeignKey(
        'households.Household',
        on_delete=models.CASCADE,
        related_name='storage_locations'
    )

    name = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['household', 'name'],
                name='unique_household_storage_location'
            )
        ]

    def __str__(self):
        return self.name


class PantryItem(models.Model):
    household = models.ForeignKey(
        'households.Household',
        on_delete=models.CASCADE,
        related_name='pantry_items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='pantry_items'
    )

    quantity = models.PositiveIntegerField(default=1)

    expiration_date = models.DateField(
        null=True,
        blank=True
    )

    storage_location = models.ForeignKey(
        StorageLocation,
        on_delete=models.PROTECT,
        related_name='pantry_items'
    )

    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} szt."


