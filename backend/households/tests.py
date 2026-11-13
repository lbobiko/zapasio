from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Household, Membership


class HouseholdAPITests(APITestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

    def test_create_household(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/households/',
            {'name': 'My Home'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        household = Household.objects.get(name='My Home')

        self.assertEqual(
            household.owner,
            self.user
        )

        self.assertTrue(
            Membership.objects.filter(
                household=household,
                user=self.user,
                role='owner'
            ).exists()
        )

    def test_user_cannot_see_other_households(self):
        User = get_user_model()

        other_user = User.objects.create_user(
            username='otheruser',
            password='testpassword123'
        )

        other_household = Household.objects.create(
            name='Other Home',
            owner=other_user
        )

        Membership.objects.create(
            user=other_user,
            household=other_household,
            role='owner'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/households/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            0
        )

    def test_member_can_see_household(self):
        household = Household.objects.create(
            name='Family Home',
            owner=self.user
        )

        Membership.objects.create(
            user=self.user,
            household=household,
            role='member'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/households/')

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
            'Family Home'
        )

    def test_member_cannot_update_household(self):
        User = get_user_model()

        owner = User.objects.create_user(
            username='owner',
            password='testpassword123'
        )

        household = Household.objects.create(
            name='Family Home',
            owner=owner
        )

        Membership.objects.create(
            user=owner,
            household=household,
            role='owner'
        )

        Membership.objects.create(
            user=self.user,
            household=household,
            role='member'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f'/api/households/{household.id}/',
            {'name': 'Changed Home'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        household.refresh_from_db()

        self.assertEqual(
            household.name,
            'Family Home'
        )

    def test_owner_can_update_household(self):
        household = Household.objects.create(
            name='Family Home',
            owner=self.user
        )

        Membership.objects.create(
            user=self.user,
            household=household,
            role='owner'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f'/api/households/{household.id}/',
            {'name': 'Our Family Home'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        household.refresh_from_db()

        self.assertEqual(
            household.name,
            'Our Family Home'
        )

    def test_member_cannot_delete_household(self):
        User = get_user_model()

        owner = User.objects.create_user(
            username='owner',
            password='testpassword123'
        )

        household = Household.objects.create(
            name='Family Home',
            owner=owner
        )

        Membership.objects.create(
            user=owner,
            household=household,
            role='owner'
        )

        Membership.objects.create(
            user=self.user,
            household=household,
            role='member'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f'/api/households/{household.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertTrue(
            Household.objects.filter(
                id=household.id
            ).exists()
        )

    def test_owner_can_delete_household(self):
        household = Household.objects.create(
            name='Family Home',
            owner=self.user
        )

        Membership.objects.create(
            user=self.user,
            household=household,
            role='owner'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f'/api/households/{household.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Household.objects.filter(
                id=household.id
            ).exists()
        )

        self.assertFalse(
            Membership.objects.filter(
                household_id=household.id
            ).exists()
        )

    def test_owner_can_add_member(self):
        User = get_user_model()

        new_user = User.objects.create_user(
            username='newmember',
            password='testpassword123'
        )

        household = Household.objects.create(
            name='Family Home',
            owner=self.user
        )

        Membership.objects.create(
            user=self.user,
            household=household,
            role='owner'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f'/api/households/{household.id}/members/',
            {'username': 'newmember'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            Membership.objects.filter(
                household=household,
                user=new_user,
                role='member'
            ).exists()
        )

    def test_member_cannot_add_member(self):
        User = get_user_model()

        owner = User.objects.create_user(
            username='owner',
            password='testpassword123'
        )

        new_user = User.objects.create_user(
            username='newmember',
            password='testpassword123'
        )

        household = Household.objects.create(
            name='Family Home',
            owner=owner
        )

        Membership.objects.create(
            user=owner,
            household=household,
            role='owner'
        )

        Membership.objects.create(
            user=self.user,
            household=household,
            role='member'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f'/api/households/{household.id}/members/',
            {'username': 'newmember'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertFalse(
            Membership.objects.filter(
                household=household,
                user=new_user
            ).exists()
        )

    def test_cannot_add_existing_member(self):
        household = Household.objects.create(
            name='Family Home',
            owner=self.user
        )

        Membership.objects.create(
            user=self.user,
            household=household,
            role='owner'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f'/api/households/{household.id}/members/',
            {'username': self.user.username},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT
        )

        self.assertEqual(
            Membership.objects.filter(
                household=household,
                user=self.user
            ).count(),
            1
        )

    def test_cannot_add_nonexistent_user(self):
        household = Household.objects.create(
            name='Family Home',
            owner=self.user
        )

        Membership.objects.create(
            user=self.user,
            household=household,
            role='owner'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f'/api/households/{household.id}/members/',
            {'username': 'unknownuser'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            Membership.objects.filter(
                household=household
            ).count(),
            1
        )

    def test_member_can_get_household_members(self):
        User = get_user_model()

        owner = User.objects.create_user(
            username='owner',
            password='testpassword123'
        )

        household = Household.objects.create(
            name='Family Home',
            owner=owner
        )

        Membership.objects.create(
            user=owner,
            household=household,
            role='owner'
        )

        Membership.objects.create(
            user=self.user,
            household=household,
            role='member'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/api/households/{household.id}/members/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            2
        )

    def test_non_member_cannot_get_household_members(self):
        User = get_user_model()

        owner = User.objects.create_user(
            username='owner',
            password='testpassword123'
        )

        household = Household.objects.create(
            name='Family Home',
            owner=owner
        )

        Membership.objects.create(
            user=owner,
            household=household,
            role='owner'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/api/households/{household.id}/members/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_owner_can_remove_member(self):
        User = get_user_model()

        member = User.objects.create_user(
            username='member',
            password='testpassword123'
        )

        household = Household.objects.create(
            name='Family Home',
            owner=self.user
        )

        Membership.objects.create(
            user=self.user,
            household=household,
            role='owner'
        )

        membership = Membership.objects.create(
            user=member,
            household=household,
            role='member'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f'/api/households/{household.id}/members/{membership.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Membership.objects.filter(
                id=membership.id
            ).exists()
        )

        self.assertTrue(
            User.objects.filter(
                id=member.id
            ).exists()
        )

    def test_member_cannot_remove_other_member(self):
        User = get_user_model()

        owner = User.objects.create_user(
            username='owner',
            password='testpassword123'
        )

        other_member = User.objects.create_user(
            username='othermember',
            password='testpassword123'
        )

        household = Household.objects.create(
            name='Family Home',
            owner=owner
        )

        Membership.objects.create(
            user=owner,
            household=household,
            role='owner'
        )

        Membership.objects.create(
            user=self.user,
            household=household,
            role='member'
        )

        membership = Membership.objects.create(
            user=other_member,
            household=household,
            role='member'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f'/api/households/{household.id}/members/{membership.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertTrue(
            Membership.objects.filter(
                id=membership.id
            ).exists()
        )

    def test_owner_cannot_remove_themselves(self):
        household = Household.objects.create(
            name='Family Home',
            owner=self.user
        )

        membership = Membership.objects.create(
            user=self.user,
            household=household,
            role='owner'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f'/api/households/{household.id}/members/{membership.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT
        )

        self.assertTrue(
            Membership.objects.filter(
                id=membership.id
            ).exists()
        )

    def test_cannot_remove_member_from_another_household(self):
        User = get_user_model()

        member = User.objects.create_user(
            username='member',
            password='testpassword123'
        )

        household1 = Household.objects.create(
            name='Home One',
            owner=self.user
        )

        household2 = Household.objects.create(
            name='Home Two',
            owner=self.user
        )

        for household in [household1, household2]:
            Membership.objects.create(
                user=self.user,
                household=household,
                role='owner'
            )

        membership = Membership.objects.create(
            user=member,
            household=household2,
            role='member'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f'/api/households/{household1.id}/members/{membership.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertTrue(
            Membership.objects.filter(
                id=membership.id
            ).exists()
        )

    def test_unauthenticated_user_cannot_get_households(self):
        response = self.client.get('/api/households/')

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN
            ]
        )

    def test_unauthenticated_user_cannot_create_household(self):
        response = self.client.post(
            '/api/households/',
            {'name': 'Unauthorized Home'},
            format='json'
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN
            ]
        )

        self.assertEqual(
            Household.objects.count(),
            0
        )

    def test_cannot_create_household_without_name(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/households/',
            {},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            Household.objects.count(),
            0
        )

        self.assertEqual(
            Membership.objects.count(),
            0
        )

    def test_cannot_assign_another_owner_when_creating_household(self):
        User = get_user_model()

        other_user = User.objects.create_user(
            username='otheruser',
            password='testpassword123'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/households/',
            {
                'name': 'Family Home',
                'owner': other_user.id
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        household = Household.objects.get(name='Family Home')

        self.assertEqual(
            household.owner,
            self.user
        )

        self.assertFalse(
            Membership.objects.filter(
                household=household,
                user=other_user
            ).exists()
        )

    def test_owner_cannot_change_household_owner(self):
        User = get_user_model()

        other_user = User.objects.create_user(
            username='otheruser',
            password='testpassword123'
        )

        household = Household.objects.create(
            name='Family Home',
            owner=self.user
        )

        Membership.objects.create(
            user=self.user,
            household=household,
            role='owner'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f'/api/households/{household.id}/',
            {'owner': other_user.id},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        household.refresh_from_db()

        self.assertEqual(
            household.owner,
            self.user
        )

    def test_non_member_cannot_update_household(self):
        User = get_user_model()

        other_user = User.objects.create_user(
            username='otheruser',
            password='testpassword123'
        )

        household = Household.objects.create(
            name='Family Home',
            owner=other_user
        )

        Membership.objects.create(
            user=other_user,
            household=household,
            role='owner'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f'/api/households/{household.id}/',
            {'name': 'Changed Home'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        household.refresh_from_db()

        self.assertEqual(
            household.name,
            'Family Home'
        )

    def test_non_member_cannot_delete_household(self):
        User = get_user_model()

        other_user = User.objects.create_user(
            username='otheruser',
            password='testpassword123'
        )

        household = Household.objects.create(
            name='Family Home',
            owner=other_user
        )

        Membership.objects.create(
            user=other_user,
            household=household,
            role='owner'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f'/api/households/{household.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertTrue(
            Household.objects.filter(
                id=household.id
            ).exists()
        )

    def test_member_can_get_household_detail(self):
        User = get_user_model()

        owner = User.objects.create_user(
            username='owner',
            password='testpassword123'
        )

        household = Household.objects.create(
            name='Family Home',
            owner=owner
        )

        Membership.objects.create(
            user=owner,
            household=household,
            role='owner'
        )

        Membership.objects.create(
            user=self.user,
            household=household,
            role='member'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/api/households/{household.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['name'],
            'Family Home'
        )

    def test_non_member_cannot_get_household_detail(self):
        User = get_user_model()

        owner = User.objects.create_user(
            username='owner',
            password='testpassword123'
        )

        household = Household.objects.create(
            name='Family Home',
            owner=owner
        )

        Membership.objects.create(
            user=owner,
            household=household,
            role='owner'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/api/households/{household.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_cannot_add_member_without_username(self):
        household = Household.objects.create(
            name='Family Home',
            owner=self.user
        )

        Membership.objects.create(
            user=self.user,
            household=household,
            role='owner'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f'/api/households/{household.id}/members/',
            {},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            Membership.objects.filter(
                household=household
            ).count(),
            1
        )

    def test_cannot_assign_owner_role_when_adding_member(self):
        User = get_user_model()

        new_user = User.objects.create_user(
            username='newmember',
            password='testpassword123'
        )

        household = Household.objects.create(
            name='Family Home',
            owner=self.user
        )

        Membership.objects.create(
            user=self.user,
            household=household,
            role='owner'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f'/api/households/{household.id}/members/',
            {
                'username': 'newmember',
                'role': 'owner'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        membership = Membership.objects.get(
            household=household,
            user=new_user
        )

        self.assertEqual(
            membership.role,
            'member'
        )

    def test_non_member_cannot_remove_household_member(self):
        User = get_user_model()

        owner = User.objects.create_user(
            username='owner',
            password='testpassword123'
        )

        member = User.objects.create_user(
            username='member',
            password='testpassword123'
        )

        household = Household.objects.create(
            name='Family Home',
            owner=owner
        )

        Membership.objects.create(
            user=owner,
            household=household,
            role='owner'
        )

        membership = Membership.objects.create(
            user=member,
            household=household,
            role='member'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f'/api/households/{household.id}/members/{membership.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertTrue(
            Membership.objects.filter(
                id=membership.id
            ).exists()
        )

    def test_non_member_cannot_add_household_member(self):
        User = get_user_model()

        owner = User.objects.create_user(
            username='owner',
            password='testpassword123'
        )

        new_user = User.objects.create_user(
            username='newmember',
            password='testpassword123'
        )

        household = Household.objects.create(
            name='Family Home',
            owner=owner
        )

        Membership.objects.create(
            user=owner,
            household=household,
            role='owner'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f'/api/households/{household.id}/members/',
            {'username': 'newmember'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertFalse(
            Membership.objects.filter(
                household=household,
                user=new_user
            ).exists()
        )