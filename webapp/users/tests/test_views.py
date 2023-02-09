# Python imports
import base64
import json
import warnings

from django.contrib.auth import get_user_model
# Django Imports
from django.test import TestCase, Client
from django.urls import reverse
# Rest framework imports
from rest_framework.test import APIRequestFactory

User = get_user_model()
warnings.filterwarnings("ignore")


class CreateUserAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.valid_payload = {
            'first_name': 'testuser',
            'last_name': 'mahajan',
            'password': 'testpassword',
            'username': 'testuser@example.com'
        }
        self.invalid_payload = {
            'first_name': '',
            'password': '',
            'username': ''
        }

    def test_create_valid_user(self):
        response = self.client.post(
            reverse('users:register'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().first_name, 'testuser')

    def test_create_invalid_user(self):
        response = self.client.post(
            reverse('users:register'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 0)


class LoginAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.post(
            reverse('users:register'),
            data=json.dumps({
                'first_name': 'testuser',
                'last_name': 'mahajan',
                'password': 'testpassword',
                'username': 'testuser@example.com'
            }),
            content_type='application/json'
        )
        self.valid_payload = {
            'password': 'testpassword',
            'username': 'testuser@example.com'
        }
        self.invalid_payload = {
            "username": ""
        }
        self.wrong_payload = {
            "username": "test@test.in",
            "password": "test"
        }

    def test_valid_login(self):
        response = self.client.post(
            reverse('users:login'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("access-token"),
                         base64.b64encode("testuser@example.com:testpassword".encode()).decode())

    def test_bad_login_data(self):
        response = self.client.post(
            reverse('users:login'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_creds_login(self):
        response = self.client.post(
            reverse('users:login'),
            data=json.dumps(self.wrong_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)


class GetUpdateUserAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = APIRequestFactory()
        self.owner = self.client.post(
            reverse('users:register'),
            data=json.dumps({
                'first_name': 'testuser',
                'last_name': 'mahajan',
                'password': 'testpassword',
                'username': 'testuser@example.com'
            }),
            content_type='application/json'
        )
        self.user = self.client.post(
            reverse('users:login'),
            data=json.dumps({
                'password': 'testpassword',
                'username': 'testuser@example.com'
            }),
            content_type='application/json'
        )
        self.valid_headers = {
            "HTTP_AUTHORIZATION": "Basic {}".format(self.user.headers.get("access-token"))
        }
        self.invalid_header = {
            "HTTP_AUTHORIZATION": "Basic {}"
        }
        self.valid_data = {
            'password': 'testpassword',
            'first_name': 'vaibhav',
            'last_name': 'mahajan',
        }
        self.invalid_data = {
            'password': '',
            'first_name': '',
            'last_name': '',
        }

    def test_get_user(self):
        response = self.client.get(
            reverse('users:details', kwargs={'userId': self.owner.json()["id"]}),
            **self.valid_headers,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content.decode())["username"], 'testuser@example.com')

    def test_get_invalid_user(self):
        response = self.client.get(
            reverse('users:details', kwargs={'userId': self.owner.json()["id"]}),
            **self.invalid_header,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_update_user(self):
        response = self.client.put(
            reverse('users:details', kwargs={'userId': self.owner.json()["id"]}),
            data=self.valid_data,
            **self.valid_headers,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)

    def test_invalid_update_user(self):
        response = self.client.put(
            reverse('users:details', kwargs={'userId': self.owner.json()["id"]}),
            data=self.invalid_data,
            **self.valid_headers,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)


class GetHelthTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_user(self):
        response = self.client.get(
            reverse('health'),
        )
        self.assertEqual(response.status_code, 200)
