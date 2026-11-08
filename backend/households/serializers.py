from rest_framework import serializers

from .models import Household


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