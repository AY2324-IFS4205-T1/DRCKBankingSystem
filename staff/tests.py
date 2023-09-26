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
        self.assertEqual(len(response["tickets"]), 3)

        self.login_staff_2()
        response = self.client.get(reverse("getClosedTickets"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(response["tickets"]), 0)

    def test_should_get_open_tickets(self):
        self.login_staff_1()
        response = self.client.get(reverse("getClosedTickets"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestApprove(TestAuthentication): # staff action
    def test_should_not_approve(self):
        response = self.client.post(reverse("ticketApprove", kwargs={'ticket_id': '123'}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.login_staff_1()
        response = self.client.post(reverse("ticketApprove", kwargs={'ticket_id': '123'}), **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("ticketApprove", kwargs={'ticket_id': approved_ticket_id}), **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("ticketApprove", kwargs={'ticket_id': rejected_ticket_id}), **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_should_approve(self):
    #     self.login_staff_1()
    #     response = self.client.post(reverse("ticketApprove", kwargs={'ticket_id': open_ticket_id}), **self.header)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestReject(TestAuthentication): # staff action
    def test_should_not_reject(self):

        response = self.client.post(reverse("ticketReject", kwargs={'ticket_id': '123'}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.login_staff_1()
        response = self.client.post(reverse("ticketReject", kwargs={'ticket_id': '123'}), **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("ticketReject", kwargs={'ticket_id': approved_ticket_id}), **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("ticketReject", kwargs={'ticket_id': rejected_ticket_id}), **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_reject(self):
        self.login_staff_1()
        response = self.client.post(reverse("ticketReject", kwargs={'ticket_id': open_ticket_id}), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTicketDetails(TestAuthentication): # staff action
    def test_should_not_tickets_details(self):

        response = self.client.get(reverse("ticketDetails", kwargs={'ticket_id': 1}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.login_staff_1()
        response = self.client.get(reverse("ticketDetails", kwargs={'ticket_id': '123'}), **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_should_ticket_details(self):
    #     self.login_staff_1()
    #     response = self.client.get(reverse("ticketDetails", kwargs={'ticket_id': open_ticket_id}), **self.header)
    #     print(response.content)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
