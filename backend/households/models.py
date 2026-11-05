from django.db import models
from django.conf import settings

class Household(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name = 'Nazwa',
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_households',
        verbose_name = 'Właściciel'
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Membership',
        related_name='households',
        verbose_name = 'Członkowie'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name = 'Data utworzenia'
    )

    class Meta:
        verbose_name = 'Gospodarstwo domowe'
        verbose_name_plural = 'Gospodarstwa domowe'

    def __str__(self):
        return self.name


class Membership(models.Model):

    ROLE_CHOICES = [
        ('owner', 'Właściciel'),
        ('member', 'Członek'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name = 'Użytkownik'
    )

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name = 'Gospodarstwo domowe'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member',
        verbose_name = 'Rola'
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name = 'Data dołączenia'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'household'],
                name='unique_user_household'
            )
        ]
        verbose_name = 'Członkostwo'
        verbose_name_plural = 'Członkostwa'

    def __str__(self):
        return f"{self.user.username} - {self.household.name}"
