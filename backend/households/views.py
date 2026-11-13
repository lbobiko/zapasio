from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Household, Membership
from .serializers import HouseholdSerializer, MembershipSerializer
from .permissions import IsHouseholdOwnerOrReadOnly

from django.db import transaction
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


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

    @action(detail=True, methods=['get', 'post'], url_path='members')
    def members(self, request, pk=None):
        household = self.get_object()

        if request.method == 'GET':
            memberships = household.memberships.select_related(
                'user'
            ).all()

            serializer = MembershipSerializer(
                memberships,
                many=True
            )

            return Response(serializer.data)

        # POST - tylko właściciel
        if household.owner_id != request.user.id:
            return Response(
                {'detail': 'Tylko właściciel może dodawać członków.'},
                status=status.HTTP_403_FORBIDDEN
            )

        username = request.data.get('username')

        if not isinstance(username, str) or not username.strip():
            return Response(
                {'username': ['Podaj nazwę użytkownika.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        User = get_user_model()

        try:
            user = User.objects.get(username=username.strip())
        except User.DoesNotExist:
            return Response(
                {'username': ['Nie znaleziono użytkownika.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Membership.objects.filter(
            household=household,
            user=user
        ).exists():
            return Response(
                {'detail': 'Użytkownik należy już do gospodarstwa.'},
                status=status.HTTP_409_CONFLICT
            )

        membership = Membership.objects.create(
            household=household,
            user=user,
            role='member'
        )

        serializer = MembershipSerializer(membership)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['delete'],
        url_path=r'members/(?P<membership_id>\d+)'
    )
    def remove_member(self, request, pk=None, membership_id=None):
        household = self.get_object()

        if household.owner_id != request.user.id:
            return Response(
                {'detail': 'Tylko właściciel może usuwać członków.'},
                status=status.HTTP_403_FORBIDDEN
            )

        membership = get_object_or_404(
            Membership,
            pk=membership_id,
            household=household
        )

        if membership.user_id == household.owner_id:
            return Response(
                {'detail': 'Nie można usunąć właściciela gospodarstwa.'},
                status=status.HTTP_409_CONFLICT
            )

        membership.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
