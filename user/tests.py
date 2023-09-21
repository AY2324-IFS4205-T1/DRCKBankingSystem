from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user.models import User

good_pass = "G00dP@55word"

# Create your tests here.
class TestRegistration(APITestCase):
    def test_should_not_register(self):
        registration_details = {
            "username": "johnsmith",
            "email": "jsmith@gmail.com",
            "phone_no": "12345678",
            "first_name": "first",
            "last_name": "last",
            "birth_date": "2023-01-01",
            "identity_no": "S1234567B",
            "address": "jurong",
            "postal_code": "123456",
            "citizenship": "Singaporean Citizen",
            "gender": "Male",
        }
        bad_passwords = ["JohnSmith1@", "Gmail1#A", good_pass*6, "G0odP@5", "password", good_pass, good_pass, "GoodP@ssword", "G00dPa55word", ]
        for password in bad_passwords:
            registration_details["password"] = password
            response = self.client.post(reverse("customerRegister"), registration_details)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertRaises(User.DoesNotExist, User.objects.get, username="johnsmith")

    def test_should_register(self):
        registration_details = {
            "username": "test",
            "email": "test@gmail.com",
            "phone_no": "12345678",
            "first_name": "first",
            "last_name": "last",
            "birth_date": "2023-01-01",
            "identity_no": "S1234567B",
            "address": "jurong",
            "postal_code": "123456",
            "citizenship": "Singaporean Citizen",
            "gender": "Male",
        }
        registration_details["password"] = good_pass
        response = self.client.post(reverse("customerRegister"), registration_details)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TestAuthentication(APITestCase):
    fixtures = ["user/tests.json"]

    def login_customer_1(self):
        login = {"username": "test1", "password": "testpassword"}
        response = self.client.post(reverse("customerLogin"), login)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.header = {"HTTP_AUTHORIZATION": f"Token {response.data['token']}"}

    def login_customer_2(self):
        login = {"username": "test2", "password": "testpassword"}
        response = self.client.post(reverse("customerLogin"), login)
        self.header = {"HTTP_AUTHORIZATION": f"Token {response.data['token']}"}

    def login_staff_1(self):
        login = {"username": "staff1", "password": "testpassword"}
        response = self.client.post(reverse("staffLogin"), login)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.header = {"HTTP_AUTHORIZATION": f"Token {response.data['token']}"}

    def login_staff_2(self):
        login = {"username": "staff2", "password": "testpassword"}
        response = self.client.post(reverse("staffLogin"), login)
        self.header = {"HTTP_AUTHORIZATION": f"Token {response.data['token']}"}

    def login_staff_3(self):
        login = {"username": "staff3", "password": good_pass}
        response = self.client.post(reverse("staffLogin"), login)
        self.header = {"HTTP_AUTHORIZATION": f"Token {response.data['token']}"}

    def login_staff_4(self):
        login = {"username": "staff4", "password": good_pass}
        response = self.client.post(reverse("staffLogin"), login)
        self.header = {"HTTP_AUTHORIZATION": f"Token {response.data['token']}"}

    def test_logins(self):
        self.login_customer_1()
        self.login_customer_2()
        self.login_staff_1()
        self.login_staff_2()
        self.login_staff_3()
        self.login_staff_4()
