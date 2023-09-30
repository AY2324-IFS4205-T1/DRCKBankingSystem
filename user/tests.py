from hashlib import sha512

import pyotp
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from user.models import TwoFA, User

good_pass = "G00dP@55word"


class TestRegistration(APITestCase):
    def test_should_not_register_nric(self):
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

    def test_should_not_register_passwords(self):
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
        bad_passwords = [
            "JohnSmith1@",
            "Gmail1#A",
            good_pass * 10,
            "G0odP@5",
            "password",
            "g00dp@55word",
            "G00DP@55WORD",
            "GoodP@ssword",
            "G00dPa55word",
        ]
        for password in bad_passwords:
            registration_details["password"] = password
            response = self.client.post(
                reverse("customerRegister"), registration_details
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertRaises(User.DoesNotExist, User.objects.get, username="johnsmith")

    def test_should_register(self):
        registration_details = {
            "username": "test",
            "email": "test@gmail.com",
            "phone_no": "12345678",
            "first_name": "first",
            "last_name": "last",
            "birth_date": "1999-01-01",
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
        login = {"username": "test1", "password": good_pass}
        response = self.client.post(reverse("customerLogin"), login)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.header = {"HTTP_AUTHORIZATION": f"Token {response.data['token']}"}

    def login_customer_2(self):
        login = {"username": "test2", "password": good_pass}
        response = self.client.post(reverse("customerLogin"), login)
        self.header = {"HTTP_AUTHORIZATION": f"Token {response.data['token']}"}

    def auth_type_check_cust(self):
        response = self.client.get(reverse("auth_check"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def login_staff_1(self):
        login = {"username": "staff1", "password": good_pass}
        response = self.client.post(reverse("staffLogin"), login)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.header = {"HTTP_AUTHORIZATION": f"Token {response.data['token']}"}

    def login_staff_2(self):
        login = {"username": "staff2", "password": good_pass}
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

    def auth_type_check_staff(self):
        response = self.client.get(reverse("auth_check"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"user_type": "Staff"})

    def test_logins(self):
        self.login_customer_1()
        self.login_customer_2()
        self.auth_type_check_cust()
        self.login_staff_1()
        self.login_staff_2()
        self.login_staff_3()
        self.login_staff_4()
        self.auth_type_check_staff()


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

    def create_two_fa_staff3(self):
        self.login_staff_3()
        response = self.client.get(reverse("setup_2fa"), **self.header)
        return response

    def create_two_fa_staff4(self):
        self.login_staff_4()
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
        self.assertEqual(response.json(), {"2FA success": False, "last_authenticated": None})

    def two_fa_customer_1(self):
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

    def two_fa_staff3(self):
        self.create_two_fa_staff3()

        user = User.objects.get(username="staff3")
        two_fa = TwoFA.objects.get(user=user)
        otp = pyotp.totp.TOTP(two_fa.key, digest=sha512, digits=8).now()
        sample_otp = {"otp": otp}

        response = self.client.post(reverse("verify_2fa"), sample_otp, **self.header)
        return response

    def two_fa_staff4(self):
        self.create_two_fa_staff4()

        user = User.objects.get(username="staff4")
        two_fa = TwoFA.objects.get(user=user)
        otp = pyotp.totp.TOTP(two_fa.key, digest=sha512, digits=8).now()
        sample_otp = {"otp": otp}

        response = self.client.post(reverse("verify_2fa"), sample_otp, **self.header)
        return response

    def test_should_verify_two_fa(self):
        response = self.two_fa_customer_1()
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestLogout(TestVerifyTwoFA):
    def logout_customer1(self):
        self.two_fa_customer_1()
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
