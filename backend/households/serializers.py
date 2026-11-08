from rest_framework import serializers

from .models import Household, Membership


class HouseholdSerializer(serializers.ModelSerializer):

    class Meta:
        model = Household
        fields = [
            'id',
            'name',
            'owner',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'owner',
            'created_at'
        ]

class MembershipSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    class Meta:
        model = Membership
        fields = [
            'id',
            'user',
            'username',
            'role',
            'joined_at'
        ]
        read_only_fields = [
            'id',
            'user',
            'role',
            'joined_at'
        ]