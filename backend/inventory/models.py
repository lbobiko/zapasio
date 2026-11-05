from django.db import models

class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name = 'Kategoria'
        verbose_name_plural = 'Kategorie'

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name = 'Nazwa'
    )

    barcode = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name = 'Kod kreskowy'
    )

    brand = models.CharField(
        max_length=100,
        blank=True,
        verbose_name = 'Marka'
    )

    category = models.ForeignKey(
            Category,
        on_delete=models.PROTECT,
        related_name='products',
        null=True,
        blank=True,
        verbose_name = 'Kategoria'
    )

    class Meta:
        verbose_name = 'Produkt'
        verbose_name_plural = 'Produkty'

    def __str__(self):
        return self.name


class StorageLocation(models.Model):
    household = models.ForeignKey(
        'households.Household',
        on_delete=models.CASCADE,
        related_name='storage_locations',
        verbose_name = 'Gospodarsto domowe'
    )

    name = models.CharField(
        max_length=100,
        verbose_name = 'Nazwa'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['household', 'name'],
                name='unique_household_storage_location'
            )
        ]
        verbose_name = 'Miejsce przechowywania'
        verbose_name_plural = 'Miejsca przechowywania'

    def __str__(self):
        return self.name


class PantryItem(models.Model):
    household = models.ForeignKey(
        'households.Household',
        on_delete=models.CASCADE,
        related_name='pantry_items',
        verbose_name = 'Gospodarsto domowe'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='pantry_items',
        verbose_name = 'Produkt'
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name = 'Ilość'
    )

    expiration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name = 'Data przydatności'
    )

    storage_location = models.ForeignKey(
        StorageLocation,
        on_delete=models.PROTECT,
        related_name='pantry_items',
        verbose_name = 'Miejsce przechowywania'
    )

    class Meta:
        verbose_name = 'Zapas'
        verbose_name_plural = 'Zapasy'

    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} szt."



