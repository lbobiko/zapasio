from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Household, Membership


class IsHouseholdOwnerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True

        if isinstance(obj, Household):
            return obj.owner_id == request.user.id

        if isinstance(obj, Membership):
            return obj.household.owner_id == request.user.id

        return False