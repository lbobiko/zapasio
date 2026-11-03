from django.db import models
from django.conf import settings

class Household(models.Model):
    name = models.CharField(max_length=100)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_households'
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Membership',
        related_name='households'
    )

    created_at = models.DateTimeField(auto_now_add=True)

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
        related_name='memberships'
    )

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member'
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'household'],
                name='unique_user_household'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.household.name}"
