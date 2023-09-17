from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


# Create your tests here.
class TestAuthentication(APITestCase):
    fixtures = ["user/tests.json"]

    def login_customer_1(self):
        login = {"username": "test1", "password": "testpassword"}
        response = self.client.post(reverse("customerLogin"), login)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['token']}")

    def login_customer_2(self):
        login = {"username": "test2", "password": "testpassword"}
        response = self.client.post(reverse("customerLogin"), login)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['token']}")

    def login_staff_1(self):
        login = {"username": "staff1", "password": "testpassword"}
        response = self.client.post(reverse("staffLogin"), login)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['token']}")

    def login_staff_2(self):
        login = {"username": "staff2", "password": "testpassword"}
        response = self.client.post(reverse("staffLogin"), login)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['token']}")

    def test_logins(self):
        self.login_customer_1()
        self.login_customer_2()
        self.login_staff_1()
        self.login_staff_2()
