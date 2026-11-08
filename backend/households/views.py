from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Household, Membership
from .serializers import HouseholdSerializer
from .permissions import IsHouseholdOwnerOrReadOnly

from django.db import transaction


class HouseholdViewSet(viewsets.ModelViewSet):
    serializer_class = HouseholdSerializer
    permission_classes = [
        IsAuthenticated,
        IsHouseholdOwnerOrReadOnly
    ]

    def get_queryset(self):
        return Household.objects.filter(
            memberships__user=self.request.user
        ).distinct()

    @transaction.atomic
    def perform_create(self, serializer):
        household = serializer.save(
            owner=self.request.user
        )

        Membership.objects.create(
            user=self.request.user,
            household=household,
            role='owner'
        )
