from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

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

from django.db.models.deletion import ProtectedError


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
        return PantryItem.objects.filter(
            household__memberships__user=self.request.user
        ).select_related(
            'product',
            'household',
            'storage_location'
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