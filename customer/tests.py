from django.urls import reverse
from rest_framework import status

from user.tests import TestAuthentication


class TestGetAccountTypes(TestAuthentication): # customer action
    def test_should_not_access_get_account_types(self):
        response = self.client.get(reverse("customerGetAccountTypes"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_access_get_account_types(self):
        self.login_customer_1()
        response = self.client.get(reverse("customerGetAccountTypes"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestApply(TestAuthentication): # customer action
    def test_should_not_apply(self):
        bad_field = {"acountType": "savings"}
        bad_type = {"account_type": "savingsssss"}

        response = self.client.post(reverse("apply"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.login_customer_1()
        response = self.client.post(reverse("apply"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("apply"), bad_type)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_apply(self):
        sample_apply = {"account_type": "Savings"}
        self.login_customer_1()
        response = self.client.post(reverse("apply"), sample_apply)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class TestGetBalance(TestAuthentication): # customer action
    def test_should_not_get_balance(self):
        response = self.client.get(reverse("balance"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_should_get_balance(self):
        self.login_customer_1()
        response = self.client.get(reverse("balance"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestDeposit(TestAuthentication): # customer action
    def test_should_not_deposit(self):
        bad_field_account_id = {"acount_iiiiid": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": 50, "description": "string"}
        bad_field_amount = {"account_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "ammmmmount": 50, "description": "string"}
        bad_field_description = {"account_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": 50, "ddddddescription": "string"}
        bad_type_account_id = {"account_id": "blah blah", "amount": 50, "description": "string"}
        bad_type_not_my_account_id = {"account_id": "315d9b27-1ba3-4ed8-a5c9-1bdfd042560c", "amount": 50, "description": "string"}
        bad_type_amount_str = {"account_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": "50abc", "description": "string"}
        bad_type_amount_2dp = {"account_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": 50.00001, "description": "string"}
        bad_type_amount_0 = {"account_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": 0, "description": "string"}
        bad_type_description_long = {"account_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": 50, "description": "a"*256}

        response = self.client.post(reverse("deposit"), bad_field_account_id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        requests = [bad_field_account_id, bad_field_amount, bad_field_description, bad_type_account_id, bad_type_not_my_account_id, bad_type_amount_str, bad_type_amount_2dp, bad_type_amount_0, bad_type_description_long]
        self.login_customer_1()
        for request in requests:
            response = self.client.post(reverse("deposit"), request)
            if response.status_code == status.HTTP_200_OK:
                print(request)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_deposit(self):
        self.login_customer_1()
        sample_deposit = {"account_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": 50, "description": "string"}
        response = self.client.post(reverse("deposit"), sample_deposit)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestWithdraw(TestAuthentication): # customer action
    def test_should_not_withdraw(self):
        bad_field_account_id = {"acount_iiiiid": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": 50, "description": "string"}
        bad_field_amount = {"account_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "ammmmmount": 50, "description": "string"}
        bad_field_description = {"account_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": 50, "ddddddescription": "string"}
        bad_type_account_id = {"account_id": "blah blah", "amount": 50, "description": "string"}
        bad_type_not_my_account_id = {"account_id": "315d9b27-1ba3-4ed8-a5c9-1bdfd042560c", "amount": 50, "description": "string"}
        bad_type_amount_str = {"account_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": "50abc", "description": "string"}
        bad_type_amount_2dp = {"account_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": 50.00001, "description": "string"}
        bad_type_amount_0 = {"account_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": 0, "description": "string"}
        bad_type_amount_too_much = {"account_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": 1000, "description": "string"}
        bad_type_description_long = {"account_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": 50, "description": "a"*256}

        response = self.client.post(reverse("withdraw"), bad_field_account_id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        requests = [bad_field_account_id, bad_field_amount, bad_field_description, bad_type_account_id, bad_type_not_my_account_id, bad_type_amount_str, bad_type_amount_2dp, bad_type_amount_0, bad_type_amount_too_much, bad_type_description_long]
        self.login_customer_1()
        for request in requests:
            response = self.client.post(reverse("withdraw"), request)
            if response.status_code == status.HTTP_200_OK:
                print(request)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_withdraw(self):
        self.login_customer_1()
        sample_withdrawal = {"account_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": 50, "description": "string"}
        response = self.client.post(reverse("withdraw"), sample_withdrawal)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTransfer(TestAuthentication): # customer action
    def test_should_not_withdraw(self):
        bad_field_sender_id = {"sssender_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "recipient_id": "315d9b27-1ba3-4ed8-a5c9-1bdfd042560c", "amount": 50, "description": "string"}
        bad_field_recipient_id = {"sender_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "rrrecipient_id": "315d9b27-1ba3-4ed8-a5c9-1bdfd042560c", "amount": 50, "description": "string"}
        bad_field_amount = {"sender_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "recipient_id": "315d9b27-1ba3-4ed8-a5c9-1bdfd042560c", "ammmount": 50, "description": "string"}
        bad_field_description = {"sender_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "recipient_id": "315d9b27-1ba3-4ed8-a5c9-1bdfd042560c", "amount": 50, "ddddescription": "string"}
        bad_type_sender_id = {"sender_id": "blah blah", "recipient_id": "315d9b27-1ba3-4ed8-a5c9-1bdfd042560c", "amount": 50, "description": "string"}
        bad_type_recipient_id = {"sender_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "recipient_id": "blah blah", "amount": 50, "description": "string"}
        bad_type_not_my_account_id = {"sender_id": "315d9b27-1ba3-4ed8-a5c9-1bdfd042560c", "recipient_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": 50, "description": "string"}
        bad_type_same_accounts = {"sender_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "recipient_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "amount": 50, "description": "string"}
        bad_type_amount_str = {"sender_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "recipient_id": "315d9b27-1ba3-4ed8-a5c9-1bdfd042560c", "amount": "50abc", "description": "string"}
        bad_type_amount_2dp = {"sender_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "recipient_id": "315d9b27-1ba3-4ed8-a5c9-1bdfd042560c", "amount": 50.000001, "description": "string"}
        bad_type_amount_0 = {"sender_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "recipient_id": "315d9b27-1ba3-4ed8-a5c9-1bdfd042560c", "amount": 0, "description": "string"}
        bad_type_amount_too_much = {"sender_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "recipient_id": "315d9b27-1ba3-4ed8-a5c9-1bdfd042560c", "amount": 1000, "description": "string"}
        bad_type_description_long = {"sender_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "recipient_id": "315d9b27-1ba3-4ed8-a5c9-1bdfd042560c", "amount": 50, "description": "a"*256}

        response = self.client.post(reverse("transfer"), bad_field_sender_id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        requests = [bad_field_sender_id, bad_field_recipient_id, bad_field_amount, bad_field_description, bad_type_sender_id, bad_type_recipient_id, bad_type_not_my_account_id, bad_type_same_accounts, bad_type_amount_str, bad_type_amount_2dp, bad_type_amount_0, bad_type_amount_too_much, bad_type_description_long]
        self.login_customer_1()
        for request in requests:
            response = self.client.post(reverse("transfer"), request)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_transfer(self):
        self.login_customer_1()
        sample_transfer = {"sender_id": "daa55c76-8b9c-4d7c-8ad9-ec485daa76f9", "recipient_id": "315d9b27-1ba3-4ed8-a5c9-1bdfd042560c", "amount": 50, "description": "string"}
        response = self.client.post(reverse("transfer"), sample_transfer)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


