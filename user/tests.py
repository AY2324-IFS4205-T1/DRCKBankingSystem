from hashlib import sha512

import pyotp
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from user.models import TwoFA, User

good_pass = "G00dP@55word"
good_registration_details = {
    "username": "johnsmith",
    "email": "jsmith@gmail.com",
    "phone_no": "12345678",
    "first_name": "first",
    "last_name": "last",
    "birth_date": "2023-01-01",
    "identity_no": "T1234567X",
    "address": "jurong",
    "postal_code": "123456",
    "citizenship": "Singaporean Citizen",
    "gender": "Male",
}

class TestRegistration(APITestCase):
    def test_should_not_register_nric(self):
        registration_details = good_registration_details.copy()
        registration_details["password"] = good_pass

        registration_details["identity_no"] = "S12345B"
        response = self.client.post(reverse("customerRegister"), registration_details)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(User.DoesNotExist, User.objects.get, username="johnsmith")

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
        registration_details = good_registration_details.copy()
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
        registration_details = good_registration_details.copy()
        registration_details["password"] = good_pass
        response = self.client.post(reverse("customerRegister"), registration_details)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = self.client.post(reverse("customerRegister"), registration_details)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


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

    def login_staff_5(self):
        login = {"username": "staff5", "password": good_pass}
        response = self.client.post(reverse("staffLogin"), login)
        self.header = {"HTTP_AUTHORIZATION": f"Token {response.data['token']}"}

    def test_logins(self):
        self.login_customer_1()
        self.login_customer_2()
        self.login_staff_1()
        self.login_staff_2()
        self.login_staff_3()
        self.login_staff_4()
        self.login_staff_5()


class TestCreateTwoFA(TestAuthentication):
    def test_should_not_create_two_fa(self):
        response = self.client.get(reverse("setup_2fa"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def create_two_fa_customer1(self):
        self.login_customer_1()
        response = self.client.get(reverse("setup_2fa"), **self.header)
        return response
    
    def create_two_fa_customer2(self):
        self.login_customer_2()
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

    def create_two_fa_staff5(self):
        self.login_staff_5()
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
        self.assertEqual(response.json(), {"2FA success": False})

    def two_fa_customer_1(self):
        self.create_two_fa_customer1()

        user = User.objects.get(username="test1")
        two_fa = TwoFA.objects.get(user=user)
        otp = pyotp.totp.TOTP(two_fa.key, digest=sha512, digits=8).now()
        sample_otp = {"otp": otp}

        response = self.client.post(reverse("verify_2fa"), sample_otp, **self.header)
        return response

    def two_fa_customer_2(self):
        self.create_two_fa_customer2()

        user = User.objects.get(username="test2")
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

    def two_fa_staff5(self):
        self.create_two_fa_staff5()

        user = User.objects.get(username="staff5")
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
        TwoFA.objects.get(user=user)


class TestAuthCheck(TestLogout):

    def test_should_not_auth_check(self):
        self.two_fa_customer_1()
        bad_field = {"paaaage_type": "Ticket Reviewer"}
        bad_value = {"page_type": "Tiiiicket Reviewer"}
        
        response = self.client.post(reverse("auth_check"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("auth_check"), bad_value, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_auth_check(self):
        # no login
        sample_customer_auth_check = {"page_type": "Customer"}
        sample_ticket_auth_check = {"page_type": "Ticket Reviewer"}

        sample_auth_check = sample_ticket_auth_check
        response = self.client.post(reverse("auth_check"), sample_auth_check)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        expected = {'authenticated': False, 'authenticated_message': 'User not logged in.', 'authorised': False, 'user_authorisation': ''}
        self.assertEqual(response.json(), expected)
        
        # login but unauthorised and no 2FA
        self.login_customer_1()
        response = self.client.post(reverse("auth_check"), sample_auth_check, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        expected = {'authenticated': False, 'authenticated_message': '', 'authorised': False, 'user_authorisation': 'Customer', 'user_role': 'Customer'}
        self.assertEqual(response.json(), expected)
        
        # login, authorised, but no 2FA
        sample_auth_check = sample_customer_auth_check
        response = self.client.post(reverse("auth_check"), sample_auth_check, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        expected = {'authenticated': False, 'authenticated_message': 'User does not have 2FA set up.', 'authorised': True, 'user_authorisation': 'Customer', 'user_role': 'Customer'}
        self.assertEqual(response.json(), expected)
        
        # login, authorised, 2FA set up but not verified
        self.create_two_fa_customer1()
        response = self.client.post(reverse("auth_check"), sample_auth_check, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        expected = {'authenticated': False, 'authenticated_message': 'User does not have 2FA set up.', 'authorised': True, 'user_authorisation': 'Customer', 'user_role': 'Customer'}
        self.assertEqual(response.json(), expected)

        # login, 2FA, but unauthorised
        self.two_fa_customer_1()
        sample_auth_check = sample_ticket_auth_check
        response = self.client.post(reverse("auth_check"), sample_auth_check, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        expected = {'authenticated': True, 'authenticated_message': '', 'authorised': False, 'user_authorisation': 'Customer', 'user_role': 'Customer'}
        self.assertEqual(response.json(), expected)
        
        # login, authorised, and 2FA
        self.two_fa_staff1()
        response = self.client.post(reverse("auth_check"), sample_auth_check, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = {'authenticated': True, 'authenticated_message': '', 'authorised': True, 'user_authorisation': 'Staff', 'user_role': 'Ticket Reviewer'}
        self.assertEqual(response.json(), expected)
