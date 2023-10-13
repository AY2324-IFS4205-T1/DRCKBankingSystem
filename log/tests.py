from django.urls import reverse
from rest_framework import status
from log.models import AccessControlLogs, ConflictOfInterestLogs, LoginLog
from staff.models import Tickets

from user.tests import TestLogout

good_start = "2023-03-09T00:00"
good_end = "2023-11-09T00:00"

class TestLoginLogging(TestLogout): # staff action
    def test_should_log(self):
        for _ in range(5):
            login = {"username": "test1", "password": "wrongpassword"}
            self.client.post(reverse("customerLogin"), login)
        logs = LoginLog.objects.all()
        self.assertEqual(len(logs), 5)

    def test_login_logs_view(self):
        sample_login_logs = {"severity": "High", "start": good_start, "end": good_end}
        bad_field_severity = {"ssssseverity": "High", "start": good_start, "end": good_end}
        bad_field_start = {"severity": "High", "sssstart": good_start, "end": good_end}
        bad_field_end = {"severity": "High", "start": good_start, "eeeeend": good_end}
        bad_value_severity = {"severity": "HHHHigh", "start": good_start, "end": good_end}
        bad_value_start = {"severity": "High", "start": "2023-0ferg00:00", "end": good_end}
        bad_value_end = {"severity": "High", "start": good_start, "end": "2023-grdnyt0:00"}
        bad_value_end_after_now = {"severity": "High", "start": good_start, "end": "2050-11-09T00:00"}
        bad_value_end_before_start = {"severity": "High", "start": "2023-09-09T00:00", "end": good_start}

        response = self.client.post(reverse("login_logs"), sample_login_logs)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_customer_1()
        response = self.client.post(reverse("login_logs"), sample_login_logs, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff1()
        response = self.client.post(reverse("login_logs"), sample_login_logs, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff3()
        response = self.client.post(reverse("login_logs"), bad_value_end_before_start, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        requests = [sample_login_logs, bad_field_severity, bad_field_start, bad_field_end, bad_value_severity, bad_value_start, bad_value_end, bad_value_end_after_now]
        for request in requests:
            response = self.client.post(reverse("login_logs"), request, **self.header)
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestAccessControlLogging(TestLogout): # staff action
    def test_should_log(self):
        self.two_fa_customer_1()
        self.client.get(reverse("staffWelcome"), **self.header)

        self.two_fa_staff1()
        self.client.get(reverse("customerWelcome"), **self.header)
        self.client.get(reverse("anonymisation"), **self.header)
        self.client.get(reverse("login_logs"), **self.header)

        self.two_fa_staff3()
        self.client.get(reverse("getOpenTickets"), **self.header)

        logs = AccessControlLogs.objects.all()
        self.assertEqual(len(logs), 5)

    def test_access_control_logs_view(self):
        sample_login_logs = {"severity": "High", "start": good_start, "end": good_end}
        bad_field_severity = {"ssssseverity": "High", "start": good_start, "end": good_end}
        bad_field_start = {"severity": "High", "sssstart": good_start, "end": good_end}
        bad_field_end = {"severity": "High", "start": good_start, "eeeeend": good_end}
        bad_value_severity = {"severity": "HHHHigh", "start": good_start, "end": good_end}
        bad_value_start = {"severity": "High", "start": "2023-0ferg00:00", "end": good_end}
        bad_value_end = {"severity": "High", "start": good_start, "end": "2023-grdnyt0:00"}
        bad_value_end_after_now = {"severity": "High", "start": good_start, "end": "2050-11-09T00:00"}
        bad_value_end_before_start = {"severity": "High", "start": "2023-09-09T00:00", "end": good_start}

        response = self.client.post(reverse("access_control_logs"), sample_login_logs)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_customer_1()
        response = self.client.post(reverse("access_control_logs"), sample_login_logs, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff1()
        response = self.client.post(reverse("access_control_logs"), sample_login_logs, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff3()
        response = self.client.post(reverse("access_control_logs"), bad_value_end_before_start, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        requests = [sample_login_logs, bad_field_severity, bad_field_start, bad_field_end, bad_value_severity, bad_value_start, bad_value_end, bad_value_end_after_now]
        for request in requests:
            response = self.client.post(reverse("access_control_logs"), request, **self.header)
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestConflictOfInterestLogging(TestLogout): # staff action
    def test_should_log(self):
        self.two_fa_customer_2()
        sample_open_ticket = {"ticket_type": "Opening Account", "value": "3"}
        self.client.post(reverse("customerTickets"), sample_open_ticket, **self.header)

        customer_2_id = "933b2980-bc5f-469c-be78-0ba4dc8fe42c"
        open_ticket_id = Tickets.objects.get(created_by=customer_2_id, status=Tickets.TicketStatus.OPEN).ticket
        self.two_fa_staff1()
        sample_approve = {"ticket_id": open_ticket_id}
        self.client.post(reverse("ticketApprove"), sample_approve, **self.header)
        
        logs = ConflictOfInterestLogs.objects.all()
        self.assertEqual(len(logs), 1)

    def test_conflict_of_interest_logs_view(self):
        sample_login_logs = {"severity": "High", "log_id": 1}
        bad_field_severity = {"ssssseverity": "High", "log_id": 1}
        bad_field_log_id = {"severity": "High", "lllllog_id": 1}
        bad_value_severity = {"severity": "HHHHigh", "log_id": 1}
        bad_value_log_id = {"severity": "High", "log_id": -1000000}

        response = self.client.post(reverse("access_control_logs"), sample_login_logs)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_customer_1()
        response = self.client.post(reverse("access_control_logs"), sample_login_logs, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff1()
        response = self.client.post(reverse("access_control_logs"), sample_login_logs, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff3()        
        requests = [sample_login_logs, bad_field_severity, bad_field_log_id, bad_value_severity, bad_value_log_id]
        for request in requests:
            response = self.client.post(reverse("access_control_logs"), request, **self.header)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
