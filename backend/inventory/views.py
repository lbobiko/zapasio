from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import (
    Product,
    Category,
    PantryItem,
    StorageLocation)
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    PantryItemSerializer,
    StorageLocationSerializer)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from django.db.models.deletion import ProtectedError
from django.db.models import Count, Q


@api_view(['GET', 'POST'])
def product_list(request):

    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        try:
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ProtectedError:
            return Response(
                {
                    'detail': 'Nie można usunąć produktu, '
                              'ponieważ jest wykorzystywany w zapasach.'
                },
                status=status.HTTP_409_CONFLICT
            )

    elif request.method == 'PUT':
        serializer = ProductSerializer(
            product,
            data=request.data
        )

    elif request.method == 'PATCH':
        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True
        )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()

        try:
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ProtectedError:
            return Response(
                {'detail': 'Nie można usunąć kategorii, '
                            'poniewaz jest przypisana do produktów'
                 },
                status = status.HTTP_409_CONFLICT
            )

class PantryItemViewSet(viewsets.ModelViewSet):
    serializer_class = PantryItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = PantryItem.objects.filter(
            household__memberships__user=self.request.user
        ).select_related(
            'product',
            'household',
            'storage_location'
        ).distinct()

        if self.action != 'list':
            return queryset

        expiration_status = self.request.query_params.get(
            'expiration_status'
        )

        valid_statuses = {
            'expired',
            'expires_today',
            'expiring_soon',
            'fresh',
            'no_date',
        }

        if expiration_status is not None and expiration_status not in valid_statuses:
            raise ValidationError({
                'expiration_status': 'Nieprawidłowy status ważności.'
            })

        if expiration_status == 'expired':
            today = timezone.localdate()
            queryset = queryset.filter(
                expiration_date__lt=today
            )

        elif expiration_status == 'fresh':
            today = timezone.localdate()
            queryset = queryset.filter(
                expiration_date__gt=today + timedelta(days=3)
            )

        elif expiration_status == 'expiring_soon':
            today = timezone.localdate()

            queryset = queryset.filter(
                expiration_date__gt=today,
                expiration_date__lte=today + timedelta(days=3)
            )

        elif expiration_status == 'expires_today':
            today = timezone.localdate()

            queryset = queryset.filter(
                expiration_date=today
            )

        elif expiration_status == 'no_date':
            queryset = queryset.filter(
                expiration_date__isnull=True
            )

        return queryset


    def perform_create(self, serializer):
        household = serializer.validated_data['household']

        if not household.memberships.filter(
            user=self.request.user
        ).exists():
            raise PermissionDenied(
                'Nie należysz do tego gospodarstwa.'
            )

        serializer.save()

    def perform_update(self, serializer):
        household = serializer.validated_data.get(
            'household',
            serializer.instance.household
        )

        if not household.memberships.filter(
            user=self.request.user
        ).exists():
            raise PermissionDenied(
                'Nie należysz do tego gospodarstwa.'
            )

        serializer.save()

    @action(detail=False, methods=['get'])
    def expiring(self, request):
        today = timezone.localdate()

        queryset = self.get_queryset().filter(
            expiration_date__lte=today + timedelta(days=3)
        ).order_by('expiration_date')

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        today = timezone.localdate()

        queryset = self.get_queryset()

        statistics = queryset.aggregate(
            total = Count('id'),
            expired = Count(
                'id',
                filter = Q(expiration_date__lt=today)
            ),
            no_date = Count(
                'id',
                filter = Q(expiration_date__isnull=True)
            ),
            expires_today = Count(
                'id',
                filter = Q(expiration_date = today)
            ),
            expiring_soon = Count(
                'id',
                filter = Q(expiration_date__gt = today) &
                         Q(expiration_date__lte = today + timedelta(days=3))
            ),
            fresh = Count(
                'id',
                filter = Q(expiration_date__gt = today + timedelta(days=3))
            )
        )

        return Response(statistics)


class StorageLocationViewSet(viewsets.ModelViewSet):
    serializer_class = StorageLocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StorageLocation.objects.filter(
            household__memberships__user=self.request.user
        ).select_related(
            'household'
        ).distinct()

    def perform_create(self, serializer):
        household = serializer.validated_data['household']

        if not household.memberships.filter(
            user=self.request.user
        ).exists():
            raise PermissionDenied(
                'Nie należysz do tego gospodarstwa.'
            )

        serializer.save()

    def perform_update(self, serializer):
        household = serializer.validated_data.get(
            'household',
            serializer.instance.household
        )

        if not household.memberships.filter(
            user=self.request.user
        ).exists():
            raise PermissionDenied(
                'Nie należysz do tego gospodarstwa.'
            )

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        storage_location = self.get_object()

        try:
            storage_location.delete()
        except ProtectedError:
            return Response(
                {
                    'detail': (
                        'Nie można usunąć miejsca przechowywania, '
                        'ponieważ znajdują się w nim zapasy.'
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )