from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    product_list,
    product_detail,
    CategoryViewSet,
    PantryItemViewSet,
    StorageLocationViewSet
)


router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register(
    'pantry-items',
    PantryItemViewSet,
    basename='pantry-item'
)
router.register(
    'storage-locations',
    StorageLocationViewSet,
    basename='storage-location'
)


urlpatterns = [
    path('products/', product_list, name='product-list'),
    path('products/<int:pk>/', product_detail, name='product-detail'),
    path('', include(router.urls)),
]