from django.urls import reverse
from rest_framework.test import APITestCase
from .models import CustomUser

# TODO: test for every exception

class BaseUserAPITest(APITestCase):
    '''Base class for all tests that requires user authentication.'''
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email = 'test@example.com',
            password = 'strongPassword123-',
            first_name = 'Test',
            last_name = 'User'
        )
        
        response = self.client.post(reverse('app_auth:token_obtain_pair'), {
            'email': 'test@example.com',
            'password': 'strongPassword123-'
        })
        
        self.token = response.data['access']
        self.auth_headers = {
            'HTTP_AUTHORIZATION': f'Bearer {self.token}'
        }


class UserCreateViewTest(APITestCase):
    ''''''
    
    def test_create_user_success(self):
        payload = {
            "email": "newuser@example.com",
            "password": "strongPassword123-",
            "first_name": "New",
            "last_name": "User"
        }
        
        response = self.client.post(reverse('user:user-create'), payload)
        self.assertEqual(response.status_code, 201)

    # TODO: test serializer


class UserListViewTest(BaseUserAPITest):
    ''''''
    
    def test_user_list_authenticated(self):
        response = self.client.get(reverse('user:user-list'), **self.auth_headers)
        
        self.assertEqual(response.status_code, 200)
        
        expected_keys = {'first_name', 'last_name', 'email'}
        self.assertTrue(expected_keys.issubset(response.data[0].keys()))


class UserReadViewTest(BaseUserAPITest):
    ''''''

    def test_user_read_authenticated(self):
        url = reverse('user:user-read', kwargs = {'pk': self.user.id})

        response = self.client.get(url, **self.auth_headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], self.user.email)


class UserUpdateViewTest(BaseUserAPITest):
    ''''''

    def test_user_update_authenticated(self):
        url = reverse('user:user-update', kwargs = {'pk': self.user.id})
        
        payload = {
            'email': 'updated@example.com',
            'first_name': self.user.first_name,
            'last_name': self.user.last_name
        }

        response = self.client.put(url, payload, **self.auth_headers)

        self.assertEqual(response.status_code, 200)


class UserDeleteViewTest(UserUpdateViewTest):
    ''''''
    
    def test_user_delete_authenticated(self):
        url = reverse('user:user-delete', kwargs = {'pk': self.user.id})
        
        response = self.client.delete(url, **self.auth_headers)
        
        self.assertEqual(response.status_code, 204)
        self.assertFalse(CustomUser.objects.filter(pk = self.user.id).exists())