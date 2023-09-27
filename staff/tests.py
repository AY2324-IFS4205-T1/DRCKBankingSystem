import json

from django.urls import reverse
from rest_framework import status

from user.tests import TestAuthentication

approved_ticket_id = "0d9cd690-5141-4e99-8fd0-992ca2ecfa9c"
rejected_ticket_id = "ce77f63a-063b-43d0-b7f3-85972b8f81c4"
open_ticket_id = "073eb525-7eb8-4ac7-a372-0955465cfb80"

class TestGetOpenTickets(TestAuthentication): # staff action
    def test_should_not_get_open_tickets(self):
        response = self.client.get(reverse("getOpenTickets"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_should_get_open_tickets(self):
        self.login_staff_1()
        response = self.client.get(reverse("getOpenTickets"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestGetClosedTickets(TestAuthentication): # staff action
    def test_should_not_get_closed_tickets(self):
        response = self.client.get(reverse("getClosedTickets"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.login_staff_1()
        response = self.client.get(reverse("getClosedTickets"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(response["closed_tickets"]), 3)

        self.login_staff_2()
        response = self.client.get(reverse("getClosedTickets"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(response["closed_tickets"]), 0)

    def test_should_get_open_tickets(self):
        self.login_staff_1()
        response = self.client.get(reverse("getClosedTickets"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestApprove(TestAuthentication): # staff action
    def test_should_not_approve(self):
        bad_field = {"tiiiiicket_id": ""}
        bad_type = {"ticket_id": ""}
        already_approved = {"ticket_id": approved_ticket_id}
        already_rejected = {"ticket_id": rejected_ticket_id}

        response = self.client.post(reverse("approve"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.login_staff_1()
        response = self.client.post(reverse("approve"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("approve"), bad_type, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("approve"), already_approved, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("approve"), already_rejected, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_approve(self):
        self.login_staff_1()
        sample_approve = {"ticket_id": open_ticket_id}
        response = self.client.post(reverse("approve"), sample_approve, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestReject(TestAuthentication): # staff action
    def test_should_not_reject(self):
        bad_field = {"tiiiiicket_id": ""}
        bad_type = {"ticket_id": ""}
        already_approved = {"ticket_id": approved_ticket_id}
        already_rejected = {"ticket_id": rejected_ticket_id}

        response = self.client.post(reverse("reject"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.login_staff_1()
        response = self.client.post(reverse("reject"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("reject"), bad_type, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("reject"), already_approved, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("reject"), already_rejected, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_reject(self):
        self.login_staff_1()
        sample_reject = {"ticket_id": open_ticket_id}
        response = self.client.post(reverse("reject"), sample_reject, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTicketDetails(TestAuthentication): # staff action
    def test_should_not_tickets_details(self):
        bad_field = {"tiiiiicket_id": ""}
        bad_type = {"ticket_id": ""}

        response = self.client.post(reverse("ticketDetails"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.login_staff_1()
        response = self.client.post(reverse("ticketDetails"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("ticketDetails"), bad_type, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_ticket_details(self):
        self.login_staff_1()
        sample_ticket_details = {"ticket_id": open_ticket_id}
        response = self.client.post(reverse("ticketDetails"), sample_ticket_details, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestAnonymisation(TestAuthentication): # staff action
    fixtures = ["generate_data/fixtures/massive_json.json"]
    def test_should_not_anonymise(self):
        bad_k_value_field = {"kkkk_value": "", "query": ""}
        bad_query_field = {"k_value": "", "qqqquery": ""}
        bad_k_value_type = {"k_value": "0", "query": ""}
        bad_query_type = {"k_value": "1", "query": ""}

        response = self.client.post(reverse("anonymisation"), bad_k_value_field)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.login_staff_1()
        response = self.client.post(reverse("anonymisation"), bad_k_value_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(reverse("anonymisation"), bad_query_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(reverse("anonymisation"), bad_k_value_type, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(reverse("anonymisation"), bad_query_type, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        

    def test_should_anonymise(self):
        self.login_staff_1()
        sample_anonymise = {"k_value": "1", "query": "1"}
        response = self.client.post(reverse("anonymisation"), sample_anonymise, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
