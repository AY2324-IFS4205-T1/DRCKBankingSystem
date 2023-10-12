
from django.urls import reverse
from rest_framework import status

from user.tests import TestLogout

good_start = "2023-03-09T00:00"
good_end = "2023-11-09T00:00"

class TestLoginLogging(TestLogout): # staff action
    def test_login_logs(self):
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


class TestAPILogging(TestLogout): # staff action
    def test_API_logs(self):
        sample_login_logs = {"severity": "High", "start": good_start, "end": good_end}
        bad_field_severity = {"ssssseverity": "High", "start": good_start, "end": good_end}
        bad_field_start = {"severity": "High", "sssstart": good_start, "end": good_end}
        bad_field_end = {"severity": "High", "start": good_start, "eeeeend": good_end}
        bad_value_severity = {"severity": "HHHHigh", "start": good_start, "end": good_end}
        bad_value_start = {"severity": "High", "start": "2023-0ferg00:00", "end": good_end}
        bad_value_end = {"severity": "High", "start": good_start, "end": "2023-grdnyt0:00"}
        bad_value_end_after_now = {"severity": "High", "start": good_start, "end": "2050-11-09T00:00"}
        bad_value_end_before_start = {"severity": "High", "start": "2023-09-09T00:00", "end": good_start}

        response = self.client.post(reverse("api_logs"), sample_login_logs)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.two_fa_customer_1()
        response = self.client.post(reverse("api_logs"), sample_login_logs, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff1()
        response = self.client.post(reverse("api_logs"), sample_login_logs, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff3()
        response = self.client.post(reverse("api_logs"), bad_value_end_before_start, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        requests = [sample_login_logs, bad_field_severity, bad_field_start, bad_field_end, bad_value_severity, bad_value_start, bad_value_end, bad_value_end_after_now]
        for request in requests:
            response = self.client.post(reverse("api_logs"), request, **self.header)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

