from django.urls import reverse
from rest_framework import status

from user.tests import TestLogout

customer1_account_id = "2f890e04-5239-418b-a7ff-42e5018af860"
customer2_account_id = "d90e5d13-b69e-47e6-aa53-abc090528401"


class TestWelcome(TestLogout):  # customer action
    def test_should_not_access_get_account_types(self):
        response = self.client.get(reverse("customerWelcome"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_staff1()
        response = self.client.get(reverse("customerWelcome"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_get_account_types(self):
        self.two_fa_customer_1()
        response = self.client.get(reverse("customerWelcome"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_two_fa_token_timeout(self):
        self.two_fa_customer_1()
        old_header = self.header
        self.logout_customer1()
        self.login_customer_1()
        response = self.client.get(reverse("customerWelcome"), **old_header)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestGetAccountTypes(TestLogout):  # customer action
    def test_should_not_access_get_account_types(self):
        response = self.client.get(reverse("customerAccountTypes"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_staff1()
        response = self.client.get(reverse("customerAccountTypes"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_get_account_types(self):
        self.two_fa_customer_1()
        response = self.client.get(reverse("customerAccountTypes"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestAccounts(TestLogout):  # customer action
    def test_should_not_get_accounts(self):
        response = self.client.get(reverse("customerAccounts"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_staff1()
        response = self.client.get(reverse("customerAccounts"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_should_get_accounts(self):
        self.two_fa_customer_1()
        response = self.client.get(reverse("customerAccounts"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTransactions(TestLogout):  # customer action
    def test_should_not_get_accounts(self):
        bad_field = {"acccount_id": customer1_account_id}
        bad_type = {"account_id": "GNsrtmtrf"}

        response = self.client.post(reverse("customerTransactions"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_staff1()
        response = self.client.post(reverse("customerTransactions"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_customer_1()
        response = self.client.post(reverse("customerTransactions"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("customerTransactions"), bad_type, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_get_accounts(self):
        self.two_fa_customer_1()
        sample_transactions = {"account_id": customer1_account_id}
        response = self.client.post(reverse("customerTransactions"), sample_transactions, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestCustomerTickets(TestLogout):  # customer action
    def test_should_not_get_tickets(self):
        response = self.client.get(reverse("customerTickets"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_staff1()
        response = self.client.get(reverse("customerTickets"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_should_get_tickets(self):
        self.two_fa_customer_1()
        response = self.client.get(reverse("customerTickets"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_should_not_create_tickets(self):
        bad_field_ticket_type = {"ttticket_type": "bsrsrb", "value": "999"}
        bad_field_value = {"ticket_type": "sgrsgr", "vaaalue": "999"}
        bad_type_ticket_type = {"ticket_type": "Opeeeening Account", "value": "999"}
        bad_value_open_account = {"ticket_type": "Opening Account", "value": "qwerfew"}
        bad_value_close_account = {"ticket_type": "Closing Account", "value": "0"}

        response = self.client.post(reverse("customerTickets"), bad_field_ticket_type)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_staff1()
        response = self.client.post(reverse("customerTickets"), bad_field_ticket_type, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_customer_1()
        response = self.client.post(reverse("customerTickets"), bad_field_ticket_type, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("customerTickets"), bad_field_value, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("customerTickets"), bad_type_ticket_type, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("customerTickets"), bad_value_open_account, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("customerTickets"), bad_value_close_account, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_open_without_repeat(self):
        sample_open_ticket = {"ticket_type": "Opening Account", "value": "1"}
        self.two_fa_customer_1()
        response = self.client.post(reverse("customerTickets"), sample_open_ticket, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse("customerTickets"), sample_open_ticket, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_close(self):
        sample_close_ticket = {"ticket_type": "Closing Account", "value": customer1_account_id}
        self.two_fa_customer_1()
        response = self.client.post(reverse("customerTickets"), sample_close_ticket, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse("customerTickets"), sample_close_ticket, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestDeposit(TestLogout):  # customer action
    def test_should_not_deposit(self):
        bad_field_account_id = {"acount_iiiiid": customer1_account_id, "amount": 50}
        bad_field_amount = {"account_id": customer1_account_id, "ammmmmount": 50}
        bad_type_account_id = {"account_id": "", "amount": 50,}
        bad_type_not_my_account_id = {"account_id": customer2_account_id, "amount": 50}
        bad_type_amount_str = {"account_id": customer1_account_id, "amount": "50abc"}
        bad_type_amount_2dp = {"account_id": customer1_account_id, "amount": 50.00001}
        bad_type_amount_0 = {"account_id": customer1_account_id, "amount": 0}

        response = self.client.post(reverse("deposit"), bad_field_account_id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_staff1()
        response = self.client.get(reverse("deposit"), bad_field_account_id, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.login_customer_1()
        response = self.client.post(reverse("deposit"), bad_field_account_id, **self.header)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_customer_1()
        requests = [
            bad_field_account_id,
            bad_field_amount,
            bad_type_account_id,
            bad_type_not_my_account_id,
            bad_type_amount_str,
            bad_type_amount_2dp,
            bad_type_amount_0,
        ]
        for request in requests:
            response = self.client.post(reverse("deposit"), request, **self.header)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_deposit(self):
        self.two_fa_customer_1()
        sample_deposit = {"account_id": customer1_account_id, "amount": 50, "description": "string"}
        response = self.client.post(reverse("deposit"), sample_deposit, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestWithdraw(TestLogout):  # customer action
    def test_should_not_withdraw(self):
        bad_field_account_id = {"acount_iiiiid": customer1_account_id, "amount": 50}
        bad_field_amount = {"account_id": customer1_account_id, "ammmmmount": 50}
        bad_type_account_id = {"account_id": "", "amount": 50}
        bad_type_not_my_account_id = {"account_id": customer2_account_id, "amount": 50}
        bad_type_amount_str = {"account_id": customer1_account_id, "amount": "50abc"}
        bad_type_amount_2dp = {"account_id": customer1_account_id, "amount": 50.00001}
        bad_type_amount_0 = {"account_id": customer1_account_id, "amount": 0}
        bad_type_amount_too_much = {"account_id": customer1_account_id, "amount": 1000}

        response = self.client.post(reverse("withdraw"), bad_field_account_id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_staff1()
        response = self.client.get(reverse("withdraw"), bad_field_account_id, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.login_customer_1()
        response = self.client.post(reverse("withdraw"), bad_field_account_id, **self.header)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_customer_1()
        requests = [
            bad_field_account_id,
            bad_field_amount,
            bad_type_account_id,
            bad_type_not_my_account_id,
            bad_type_amount_str,
            bad_type_amount_2dp,
            bad_type_amount_0,
            bad_type_amount_too_much,
        ]
        for request in requests:
            response = self.client.post(reverse("withdraw"), request, **self.header)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_withdraw(self):
        self.two_fa_customer_1()
        sample_withdrawal = {"account_id": customer1_account_id, "amount": 20, "description": "string",}
        response = self.client.post(reverse("withdraw"), sample_withdrawal, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTransfer(TestLogout):  # customer action
    def test_should_not_withdraw(self):
        bad_field_sender_id = {
            "sssender_id": customer1_account_id,
            "recipient_id": customer2_account_id,
            "amount": 50,
            "description": "string",
        }
        bad_field_recipient_id = {
            "sender_id": customer1_account_id,
            "rrrecipient_id": customer2_account_id,
            "amount": 50,
            "description": "string",
        }
        bad_field_amount = {
            "sender_id": customer1_account_id,
            "recipient_id": customer2_account_id,
            "ammmount": 50,
            "description": "string",
        }
        bad_field_description = {
            "sender_id": customer1_account_id,
            "recipient_id": customer2_account_id,
            "amount": 50,
            "ddddescription": "string",
        }
        bad_type_sender_id = {
            "sender_id": "",
            "recipient_id": customer2_account_id,
            "amount": 50,
            "description": "string",
        }
        bad_type_recipient_id = {
            "sender_id": customer1_account_id,
            "recipient_id": "",
            "amount": 50,
            "description": "string",
        }
        bad_type_not_my_account_id = {
            "sender_id": customer2_account_id,
            "recipient_id": customer1_account_id,
            "amount": 50,
            "description": "string",
        }
        bad_type_same_accounts = {
            "sender_id": customer1_account_id,
            "recipient_id": customer1_account_id,
            "amount": 50,
            "description": "string",
        }
        bad_type_amount_str = {
            "sender_id": customer1_account_id,
            "recipient_id": customer2_account_id,
            "amount": "50abc",
            "description": "string",
        }
        bad_type_amount_2dp = {
            "sender_id": customer1_account_id,
            "recipient_id": customer2_account_id,
            "amount": 50.000001,
            "description": "string",
        }
        bad_type_amount_0 = {
            "sender_id": customer1_account_id,
            "recipient_id": customer2_account_id,
            "amount": 0,
            "description": "string",
        }
        bad_type_amount_too_much = {
            "sender_id": customer1_account_id,
            "recipient_id": customer2_account_id,
            "amount": 1000,
            "description": "string",
        }
        bad_type_description_long = {
            "sender_id": customer1_account_id,
            "recipient_id": customer2_account_id,
            "amount": 50,
            "description": "a" * 256,
        }

        response = self.client.post(reverse("transfer"), bad_field_sender_id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_staff1()
        response = self.client.get(reverse("transfer"), bad_field_sender_id, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.login_customer_1()
        response = self.client.post(reverse("transfer"), bad_field_sender_id, **self.header)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_customer_1()
        requests = [
            bad_field_sender_id,
            bad_field_recipient_id,
            bad_field_amount,
            bad_field_description,
            bad_type_sender_id,
            bad_type_recipient_id,
            bad_type_not_my_account_id,
            bad_type_same_accounts,
            bad_type_amount_str,
            bad_type_amount_2dp,
            bad_type_amount_0,
            bad_type_amount_too_much,
            bad_type_description_long,
        ]
        for request in requests:
            response = self.client.post(reverse("transfer"), request, **self.header)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_transfer(self):
        self.two_fa_customer_1()
        sample_transfer = {"sender_id": customer1_account_id, "recipient_id": customer2_account_id, "amount": 10, "description": "string",}
        response = self.client.post(reverse("transfer"), sample_transfer, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
