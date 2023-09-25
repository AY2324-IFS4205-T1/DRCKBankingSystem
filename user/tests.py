from hashlib import sha512

import pyotp
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from user.models import TwoFA, User


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

    def create_two_fa_customer1(self):
        self.login_customer_1()
        response = self.client.get(reverse("setup_2fa"), **self.header)
        return response

    def create_two_fa_staff1(self):
        self.login_staff_1()
        response = self.client.get(reverse("setup_2fa"), **self.header)
        return response

    def create_two_fa_staff2(self):
        self.login_staff_2()
        response = self.client.get(reverse("setup_2fa"), **self.header)
        return response

    def test_should_create_two_fa(self):
        response = self.create_two_fa_customer1()
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestVerifyTwoFA(TestCreateTwoFA):
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
        self.assertEqual(response.json(), {"result": False, "last_authenticated": None})

    def two_fa_customer1(self):
        self.create_two_fa_customer1()

        user = User.objects.get(username="test1")
        two_fa = TwoFA.objects.get(user=user)
        otp = pyotp.totp.TOTP(two_fa.key, digest=sha512, digits=8).now()
        sample_otp = {"otp": otp}

        response = self.client.post(reverse("verify_2fa"), sample_otp, **self.header)
        return response

    def two_fa_staff1(self):
        self.create_two_fa_staff1()

        user = User.objects.get(username="staff1")
        two_fa = TwoFA.objects.get(user=user)
        otp = pyotp.totp.TOTP(two_fa.key, digest=sha512, digits=8).now()
        sample_otp = {"otp": otp}

        response = self.client.post(reverse("verify_2fa"), sample_otp, **self.header)
        return response

    def two_fa_staff2(self):
        self.create_two_fa_staff2()

        user = User.objects.get(username="staff2")
        two_fa = TwoFA.objects.get(user=user)
        otp = pyotp.totp.TOTP(two_fa.key, digest=sha512, digits=8).now()
        sample_otp = {"otp": otp}

        response = self.client.post(reverse("verify_2fa"), sample_otp, **self.header)
        return response

    def test_should_verify_two_fa(self):
        response = self.two_fa_customer1()
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestLogout(TestVerifyTwoFA):
    def logout_customer1(self):
        self.two_fa_customer1()
        response = self.client.post(reverse("logout"), **self.header)
        return response

    def logout_staff1(self):
        self.two_fa_staff1()
        response = self.client.post(reverse("logout"), **self.header)
        return response

    def test_logout(self):
        response = self.logout_customer1()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user = User.objects.get(username="test1")
        two_fa = TwoFA.objects.get(user=user)
        self.assertEqual(two_fa.last_authenticated, None)
