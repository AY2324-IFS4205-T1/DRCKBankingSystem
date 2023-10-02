import json

from django.urls import reverse
from rest_framework import status

from user.tests import TestLogout

approved_ticket_id = "367bffbc-87dd-4d6b-b060-5747d6509b54"
rejected_ticket_id = "7fe0efae-482f-4dfb-b5e0-b3198b1d2f3a"
open_ticket_id = "68023295-ca4c-435d-9d45-2b9b1ef1ba34"

class TestWelcome(TestLogout): # staff action
    def test_should_not_get_open_tickets(self):
        response = self.client.get(reverse("staffWelcome"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        self.two_fa_customer_1()
        response = self.client.get(reverse("staffWelcome"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_should_get_open_tickets(self):
        self.two_fa_staff1()
        response = self.client.get(reverse("staffWelcome"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestGetOpenTickets(TestLogout): # staff action
    def test_should_not_get_open_tickets(self):
        response = self.client.get(reverse("getOpenTickets"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        self.two_fa_customer_1()
        response = self.client.get(reverse("getOpenTickets"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.two_fa_staff3()
        response = self.client.get(reverse("getOpenTickets"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_should_get_open_tickets(self):
        self.two_fa_staff1()
        response = self.client.get(reverse("getOpenTickets"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestGetClosedTickets(TestLogout): # staff action
    def test_should_not_get_closed_tickets(self):
        response = self.client.get(reverse("getClosedTickets"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_staff1()
        response = self.client.get(reverse("getClosedTickets"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(response["tickets"]), 3)

        self.two_fa_staff2()
        response = self.client.get(reverse("getClosedTickets"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(response["tickets"]), 0)
        
        self.two_fa_customer_1()
        response = self.client.get(reverse("getClosedTickets"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.two_fa_staff3()
        response = self.client.get(reverse("getClosedTickets"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_should_get_open_tickets(self):
        self.two_fa_staff1()
        response = self.client.get(reverse("getClosedTickets"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestApprove(TestLogout): # staff action
    def test_should_not_approve(self):
        bad_field = {"ttticket_type": "bsrsrb"}
        bad_value_nonsense = {"ticket_type": "bsrsrb"}
        bad_value_already_approved = {"ticket_type": approved_ticket_id}
        bad_value_already_rejcted = {"ticket_type": rejected_ticket_id}

        response = self.client.post(reverse("ticketApprove"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_customer_1()
        response = self.client.post(reverse("ticketApprove"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff3()
        response = self.client.post(reverse("ticketApprove"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff1()
        response = self.client.post(reverse("ticketApprove"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(reverse("ticketApprove"), bad_value_nonsense, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(reverse("ticketApprove"), bad_value_already_approved, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(reverse("ticketApprove"), bad_value_already_rejcted, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.logout_staff1()
        response = self.client.post(reverse("ticketApprove"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_should_approve(self):
        self.two_fa_staff1()
        sample_approve = {"ticket_id": open_ticket_id}
        response = self.client.post(reverse("ticketApprove"), sample_approve, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestReject(TestLogout): # staff action
    def test_should_not_reject(self):
        bad_field = {"ttticket_type": "bsrsrb"}
        bad_value_nonsense = {"ticket_type": "bsrsrb"}
        bad_value_already_approved = {"ticket_type": approved_ticket_id}
        bad_value_already_rejcted = {"ticket_type": rejected_ticket_id}

        response = self.client.post(reverse("ticketReject"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_customer_1()
        response = self.client.post(reverse("ticketReject"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff3()
        response = self.client.post(reverse("ticketReject"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff1()
        response = self.client.post(reverse("ticketReject"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(reverse("ticketReject"), bad_value_nonsense, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(reverse("ticketReject"), bad_value_already_approved, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(reverse("ticketReject"), bad_value_already_rejcted, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.logout_staff1()
        response = self.client.post(reverse("ticketReject"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_should_reject(self):
        self.two_fa_staff1()
        sample_approve = {"ticket_id": open_ticket_id}
        response = self.client.post(reverse("ticketReject"), sample_approve, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTicketDetails(TestLogout): # staff action
    def test_should_not_tickets_details(self):
        bad_field = {"ttticket_id": "vabsrnr"}
        bad_value = {"ticket_id": "vabsrnr"}

        response = self.client.post(reverse("ticketDetails"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_customer_1()
        response = self.client.post(reverse("ticketDetails"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff3()
        response = self.client.post(reverse("ticketDetails"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.login_staff_1()
        response = self.client.post(reverse("ticketDetails"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_staff1()
        response = self.client.post(reverse("ticketDetails"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(reverse("ticketDetails"), bad_value, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_ticket_details(self):
        self.two_fa_staff1()
        sample_ticket_details = {"ticket_id": open_ticket_id}
        response = self.client.post(reverse("ticketDetails"), sample_ticket_details, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestAnonymisation(TestLogout): # staff action
    def test_should_not_anonymise(self):
        bad_k_value_field = {"kkkk_value": "", "query": ""}
        bad_query_field = {"k_value": "", "qqqquery": ""}
        bad_k_value_type = {"k_value": "0", "query": ""}
        bad_query_type = {"k_value": "1", "query": ""}

        response = self.client.post(reverse("anonymisation"), bad_k_value_field)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_customer_1()
        response = self.client.post(reverse("anonymisation"), bad_k_value_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff2()
        response = self.client.post(reverse("anonymisation"), bad_k_value_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff4()
        response = self.client.post(reverse("anonymisation"), bad_k_value_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(reverse("anonymisation"), bad_query_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(reverse("anonymisation"), bad_k_value_type, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post(reverse("anonymisation"), bad_query_type, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_should_anonymise(self):
        self.two_fa_staff4()
        sample_anonymise = {"k_value": "1", "query": "1"}
        response = self.client.post(reverse("anonymisation"), sample_anonymise, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
