from django.contrib import admin
from .models import Household, Membership


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'created_at')
    search_fields = ('name', 'owner__username')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'household', 'role', 'joined_at')
    list_filter = ('role', 'household')
