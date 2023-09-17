import json

from django.urls import reverse
from rest_framework import status

from user.tests import TestAuthentication


class TestGetOpenTickets(TestAuthentication): # staff action
    def test_should_not_get_open_tickets(self):
        response = self.client.get(reverse("getOpenTickets"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_should_get_open_tickets(self):
        self.login_staff_1()
        response = self.client.get(reverse("getOpenTickets"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestGetClosedTickets(TestAuthentication): # staff action
    def test_should_not_get_closed_tickets(self):
        response = self.client.get(reverse("getClosedTickets"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.login_staff_1()
        response = self.client.get(reverse("getClosedTickets"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(response["closed_tickets"]), 3)

        self.login_staff_2()
        response = self.client.get(reverse("getClosedTickets"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(response["closed_tickets"]), 0)

    def test_should_get_open_tickets(self):
        self.login_staff_1()
        response = self.client.get(reverse("getClosedTickets"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestApprove(TestAuthentication): # staff action
    def test_should_not_approve(self):
        bad_field = {"tiiiiicket_id": "blah blah"}
        bad_type = {"ticket_id": "blah blah"}
        already_approved = {"ticket_id": "0d9cd690-5141-4e99-8fd0-992ca2ecfa9c"}
        already_rejected = {"ticket_id": "ce77f63a-063b-43d0-b7f3-85972b8f81c4"}

        response = self.client.post(reverse("approve"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.login_staff_1()
        response = self.client.post(reverse("approve"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("approve"), bad_type)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("approve"), already_approved)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("approve"), already_rejected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_approve(self):
        self.login_staff_1()
        sample_approve = {"ticket_id": "073eb525-7eb8-4ac7-a372-0955465cfb80"}
        response = self.client.post(reverse("approve"), sample_approve)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestReject(TestAuthentication): # staff action
    def test_should_not_reject(self):
        bad_field = {"tiiiiicket_id": "blah blah"}
        bad_type = {"ticket_id": "blah blah"}
        already_approved = {"ticket_id": "0d9cd690-5141-4e99-8fd0-992ca2ecfa9c"}
        already_rejected = {"ticket_id": "ce77f63a-063b-43d0-b7f3-85972b8f81c4"}

        response = self.client.post(reverse("reject"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.login_staff_1()
        response = self.client.post(reverse("reject"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("reject"), bad_type)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("reject"), already_approved)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("reject"), already_rejected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_reject(self):
        self.login_staff_1()
        sample_reject = {"ticket_id": "073eb525-7eb8-4ac7-a372-0955465cfb80"}
        response = self.client.post(reverse("reject"), sample_reject)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

