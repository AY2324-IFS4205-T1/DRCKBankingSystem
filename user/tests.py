from hashlib import sha512

import pyotp
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from user.models import TwoFA, User
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
            "identity_no": "F1234567B",
            "address": "jurong",
            "postal_code": "123456",
            "citizenship": "Singaporean Citizen",
            "gender": "Male",
        }
        registration_details["password"] = good_pass
        response = self.client.post(reverse("customerRegister"), registration_details)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(User.DoesNotExist, User.objects.get, username="johnsmith")
        
        registration_details["identity_no"] = "S12345B"
        response = self.client.post(reverse("customerRegister"), registration_details)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        registration_details["identity_no"] = "A1234567B"
        response = self.client.post(reverse("customerRegister"), registration_details)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        registration_details["identity_no"] = "S12345678"
        response = self.client.post(reverse("customerRegister"), registration_details)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        registration_details["birth_date"] = "1999-01-01"
        registration_details["identity_no"] = "T1234567B"
        response = self.client.post(reverse("customerRegister"), registration_details)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(User.DoesNotExist, User.objects.get, username="johnsmith")

        registration_details["birth_date"] = "2000-01-01"
        registration_details["identity_no"] = "S1234567B"
        response = self.client.post(reverse("customerRegister"), registration_details)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(User.DoesNotExist, User.objects.get, username="johnsmith")


        registration_details["citizenship"] = "Non-Singaporean"
        response = self.client.post(reverse("customerRegister"), registration_details)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(User.DoesNotExist, User.objects.get, username="johnsmith")

# Create your tests here.
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.header = {"HTTP_AUTHORIZATION": f"Token {response.data['token']}"}

    def login_staff_1(self):
        login = {"username": "staff1", "password": "testpassword"}
        response = self.client.post(reverse("staffLogin"), login)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.header = {"HTTP_AUTHORIZATION": f"Token {response.data['token']}"}

    def login_staff_2(self):
        login = {"username": "staff2", "password": "testpassword"}
        response = self.client.post(reverse("staffLogin"), login)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.header = {"HTTP_AUTHORIZATION": f"Token {response.data['token']}"}

    def test_logins(self):
        self.login_customer_1()
        self.login_customer_2()
        self.login_staff_1()
        self.login_staff_2()


class TestCreateTwoFA(TestAuthentication):
    def test_should_not_create_two_fa(self):
        response = self.client.get(reverse("setup_2fa"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_should_create_two_fa(self):
        self.login_customer_1()
        response = self.client.get(reverse("setup_2fa"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestVerifyTwoFA(TestAuthentication):
    def test_should_not_verify_two_fa(self):
        bad_field = {"otppp": "123"}
        bad_length = {"otp": "123"}
        bad_type = {"otp": "abcdefgh"}
        wrong_otp = {"otp": "12345678"}

        response = self.client.post(reverse("verify_2fa"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.login_customer_1()
        response = self.client.post(reverse("verify_2fa"), wrong_otp, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        self.client.get(reverse("setup_2fa"), **self.header)
        response = self.client.post(reverse("verify_2fa"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(reverse("verify_2fa"), bad_length, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(reverse("verify_2fa"), bad_type, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(reverse("verify_2fa"), wrong_otp, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'result': False})
        
    
    def test_should_verify_two_fa(self):
        self.login_customer_1()
        self.client.get(reverse("setup_2fa"), **self.header)

        user = User.objects.get(username="test1")
        two_fa = TwoFA.objects.get(user=user)
        otp = pyotp.totp.TOTP(two_fa.key, digest=sha512, digits=8).now()
        sample_otp = {"otp": otp}

        response = self.client.post(reverse("verify_2fa"), sample_otp, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
