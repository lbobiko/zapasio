from rest_framework.test import APITestCase
from rest_framework import status

from .models import Product, StorageLocation, PantryItem
from households.models import Household, Membership

from django.contrib.auth import get_user_model


class ProductAPITests(APITestCase):

    def setUp(self):
        self.product = Product.objects.create(
            name="Milk",
            brand="Mlekovita"
        )

    def test_get_products(self):
        response = self.client.get('/api/products/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]['name'],
            'Milk'
        )

        self.assertEqual(
            response.data[0]['brand'],
            'Mlekovita'
        )

    def test_create_product(self):
        data = {
            'name': 'Butter',
            'brand': 'Łaciate'
        }

        response = self.client.post(
            '/api/products/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            Product.objects.count(),
            2
        )

        self.assertTrue(
            Product.objects.filter(name='Butter').exists()
        )

    def test_create_product_without_name(self):
        data = {
            'brand': 'Mlekovita'
        }

        response = self.client.post(
            '/api/products/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            Product.objects.count(),
            1
        )

    def test_update_product_brand(self):
        data = {
            'brand': 'Łaciate'
        }

        response = self.client.patch(
            f'/api/products/{self.product.id}/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.brand,
            'Łaciate'
        )

        self.assertEqual(
            self.product.name,
            'Milk'
        )

    def test_delete_product(self):
        response = self.client.delete(
            f'/api/products/{self.product.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Product.objects.filter(
                id=self.product.id
            ).exists()
        )


class PantryItemPermissionTests(APITestCase):

    def setUp(self):
        User = get_user_model()

        self.user1 = User.objects.create_user(
            username='user1',
            password='testpassword123'
        )

        self.user2 = User.objects.create_user(
            username='user2',
            password='testpassword123'
        )

        self.household = Household.objects.create(
            name='Test Household',
            owner=self.user1
        )

        Membership.objects.create(
            user=self.user1,
            household=self.household,
            role='owner'
        )

        self.product = Product.objects.create(
            name='Milk',
            brand='Mlekovita'
        )

        self.storage_location = StorageLocation.objects.create(
            household=self.household,
            name='Fridge'
        )

        self.pantry_item = PantryItem.objects.create(
            household=self.household,
            product=self.product,
            storage_location=self.storage_location,
            quantity=2
        )

    def test_unauthenticated_user_cannot_get_pantry_items(self):
        response = self.client.get('/api/pantry-items/')

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN
            ]
        )

    def test_authenticated_user_can_get_pantry_items(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get('/api/pantry-items/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

    def test_non_member_cannot_see_pantry_items(self):
        self.client.force_authenticate(user=self.user2)

        response = self.client.get('/api/pantry-items/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            0
        )

    def test_non_member_cannot_get_pantry_item_detail(self):
        self.client.force_authenticate(user=self.user2)

        response = self.client.get(
            f'/api/pantry-items/{self.pantry_item.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_owner_can_get_pantry_item_detail(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(
            f'/api/pantry-items/{self.pantry_item.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['quantity'],
            2
        )

    def test_member_can_get_pantry_items(self):
        Membership.objects.create(
            user=self.user2,
            household=self.household,
            role='member'
        )

        self.client.force_authenticate(user=self.user2)

        response = self.client.get('/api/pantry-items/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

    def test_non_member_cannot_create_pantry_item(self):
        self.client.force_authenticate(user=self.user2)

        data = {
            'household': self.household.id,
            'product': self.product.id,
            'storage_location': self.storage_location.id,
            'quantity': 5
        }

        response = self.client.post(
            '/api/pantry-items/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertEqual(
            PantryItem.objects.count(),
            1
        )

    def test_member_can_create_pantry_item(self):
        Membership.objects.create(
            user=self.user2,
            household=self.household,
            role='member'
        )

        self.client.force_authenticate(user=self.user2)

        data = {
            'household': self.household.id,
            'product': self.product.id,
            'storage_location': self.storage_location.id,
            'quantity': 5
        }

        response = self.client.post(
            '/api/pantry-items/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            PantryItem.objects.count(),
            2
        )

    def test_non_member_cannot_update_pantry_item(self):
        self.client.force_authenticate(user=self.user2)

        response = self.client.patch(
            f'/api/pantry-items/{self.pantry_item.id}/',
            {'quantity': 10},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.pantry_item.refresh_from_db()

        self.assertEqual(
            self.pantry_item.quantity,
            2
        )

    def test_member_can_update_pantry_item(self):
        Membership.objects.create(
            user=self.user2,
            household=self.household,
            role='member'
        )

        self.client.force_authenticate(user=self.user2)

        response = self.client.patch(
            f'/api/pantry-items/{self.pantry_item.id}/',
            {'quantity': 10},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.pantry_item.refresh_from_db()

        self.assertEqual(
            self.pantry_item.quantity,
            10
        )

    def test_non_member_cannot_delete_pantry_item(self):
        self.client.force_authenticate(user=self.user2)

        response = self.client.delete(
            f'/api/pantry-items/{self.pantry_item.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertTrue(
            PantryItem.objects.filter(
                id=self.pantry_item.id
            ).exists()
        )

    def test_member_can_delete_pantry_item(self):
        Membership.objects.create(
            user=self.user2,
            household=self.household,
            role='member'
        )

        self.client.force_authenticate(user=self.user2)

        response = self.client.delete(
            f'/api/pantry-items/{self.pantry_item.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            PantryItem.objects.filter(
                id=self.pantry_item.id
            ).exists()
        )

    def test_cannot_create_pantry_item_with_foreign_storage_location(self):
        other_household = Household.objects.create(
            name='Other Household',
            owner=self.user2
        )

        other_location = StorageLocation.objects.create(
            household=other_household,
            name='Other Fridge'
        )

        self.client.force_authenticate(user=self.user1)

        data = {
            'household': self.household.id,
            'product': self.product.id,
            'storage_location': other_location.id,
            'quantity': 3
        }

        response = self.client.post(
            '/api/pantry-items/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            PantryItem.objects.count(),
            1
        )

    def test_cannot_update_pantry_item_with_foreign_storage_location(self):
        other_household = Household.objects.create(
            name='Other Household',
            owner=self.user2
        )

        other_location = StorageLocation.objects.create(
            household=other_household,
            name='Other Fridge'
        )

        self.client.force_authenticate(user=self.user1)

        response = self.client.patch(
            f'/api/pantry-items/{self.pantry_item.id}/',
            {'storage_location': other_location.id},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.pantry_item.refresh_from_db()

        self.assertEqual(
            self.pantry_item.storage_location_id,
            self.storage_location.id
        )

    def test_cannot_create_pantry_item_with_negative_quantity(self):
        self.client.force_authenticate(user=self.user1)

        data = {
            'household': self.household.id,
            'product': self.product.id,
            'storage_location': self.storage_location.id,
            'quantity': -5
        }

        response = self.client.post(
            '/api/pantry-items/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            PantryItem.objects.count(),
            1
        )

# ------------- testy dla miejsc przechowywania -----------------
class StorageLocationAPITests(APITestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

        self.household = Household.objects.create(
            name='Test Household',
            owner=self.user
        )

        Membership.objects.create(
            user=self.user,
            household=self.household,
            role='owner'
        )

        self.location = StorageLocation.objects.create(
            household=self.household,
            name='Fridge'
        )

    def test_member_can_get_storage_locations(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/storage-locations/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]['name'],
            'Fridge'
        )

    def test_non_member_cannot_see_storage_locations(self):
        User = get_user_model()

        other_user = User.objects.create_user(
            username='otheruser',
            password='testpassword123'
        )

        self.client.force_authenticate(user=other_user)

        response = self.client.get('/api/storage-locations/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            0
        )

    def test_cannot_delete_storage_location_with_pantry_items(self):
        product = Product.objects.create(
            name='Milk',
            brand='Mlekovita'
        )

        PantryItem.objects.create(
            household=self.household,
            product=product,
            storage_location=self.location,
            quantity=2
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f'/api/storage-locations/{self.location.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT
        )

        self.assertTrue(
            StorageLocation.objects.filter(
                id=self.location.id
            ).exists()
        )

    def test_can_delete_empty_storage_location(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f'/api/storage-locations/{self.location.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            StorageLocation.objects.filter(
                id=self.location.id
            ).exists()
        )

    def test_cannot_change_storage_location_household(self):
        other_household = Household.objects.create(
            name='Other Household',
            owner=self.user
        )

        Membership.objects.create(
            user=self.user,
            household=other_household,
            role='owner'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f'/api/storage-locations/{self.location.id}/',
            {'household': other_household.id},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.location.refresh_from_db()

        self.assertEqual(
            self.location.household_id,
            self.household.id
        )

    def test_member_can_create_storage_location(self):
        self.client.force_authenticate(user=self.user)

        data = {
            'household': self.household.id,
            'name': 'Kitchen Cabinet'
        }

        response = self.client.post(
            '/api/storage-locations/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            StorageLocation.objects.count(),
            2
        )

        self.assertTrue(
            StorageLocation.objects.filter(
                household=self.household,
                name='Kitchen Cabinet'
            ).exists()
        )

    def test_non_member_cannot_create_storage_location(self):
        User = get_user_model()

        other_user = User.objects.create_user(
            username='otheruser',
            password='testpassword123'
        )

        self.client.force_authenticate(user=other_user)

        data = {
            'household': self.household.id,
            'name': 'Freezer'
        }

        response = self.client.post(
            '/api/storage-locations/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertEqual(
            StorageLocation.objects.count(),
            1
        )

    def test_member_can_update_storage_location(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f'/api/storage-locations/{self.location.id}/',
            {'name': 'Kitchen Fridge'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.location.refresh_from_db()

        self.assertEqual(
            self.location.name,
            'Kitchen Fridge'
        )

        self.assertEqual(
            self.location.household_id,
            self.household.id
        )

    def test_non_member_cannot_update_storage_location(self):
        User = get_user_model()

        other_user = User.objects.create_user(
            username='otheruser',
            password='testpassword123'
        )

        self.client.force_authenticate(user=other_user)

        response = self.client.patch(
            f'/api/storage-locations/{self.location.id}/',
            {'name': 'Changed Fridge'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.location.refresh_from_db()

        self.assertEqual(
            self.location.name,
            'Fridge'
        )

    def test_non_member_cannot_delete_storage_location(self):
        User = get_user_model()

        other_user = User.objects.create_user(
            username='otheruser',
            password='testpassword123'
        )

        self.client.force_authenticate(user=other_user)

        response = self.client.delete(
            f'/api/storage-locations/{self.location.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertTrue(
            StorageLocation.objects.filter(
                id=self.location.id
            ).exists()
        )