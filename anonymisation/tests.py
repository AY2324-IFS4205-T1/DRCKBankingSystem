from django.urls import reverse
from rest_framework import status

from user.tests import TestLogout
from anonymisation.models import Statistics


class TestCalculateAnon(TestLogout): # staff action
    def test_should_not_calculate_anon(self):
        response = self.client.get(reverse("calculate_anon"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        self.two_fa_customer_1()
        response = self.client.get(reverse("calculate_anon"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.two_fa_staff4()
        response = self.client.get(reverse("calculate_anon"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def calculate_anon(self):
        self.two_fa_staff5()
        response = self.client.get(reverse("calculate_anon"), **self.header)
        return response

    def test_should_calculate_anon(self):
        response = self.calculate_anon()
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestViewAnonStats(TestCalculateAnon): # staff action
    def test_should_not_view_anon_stats(self):
        response = self.client.get(reverse("view_anon_stats"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        self.two_fa_customer_1()
        response = self.client.get(reverse("view_anon_stats"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.two_fa_staff4()
        response = self.client.get(reverse("view_anon_stats"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_should_view_anon_stats(self):
        self.calculate_anon()
        self.two_fa_staff5()
        response = self.client.get(reverse("view_anon_stats"), **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestSetKValue(TestViewAnonStats): # staff action
    def test_should_not_set_k_value(self):
        bad_field = {"kkkk_value": "3"}
        bad_value_non_integer = {"k_value": "vea"}
        bad_value_non_valid = {"k_value": "1"}

        response = self.client.post(reverse("set_k"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        self.two_fa_customer_1()
        response = self.client.post(reverse("set_k"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.two_fa_staff4()
        response = self.client.post(reverse("set_k"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff5()
        response = self.client.post(reverse("set_k"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("set_k"), bad_value_non_integer, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("set_k"), bad_value_non_valid, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def set_k_value(self):
        self.calculate_anon()
        sample_set_k = {"k_value": "3"}
        self.two_fa_staff5()
        response = self.client.post(reverse("set_k"), sample_set_k, **self.header)
        return response

    def test_should_set_k_value(self):
        response = self.set_k_value()
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestQueryAnon(TestSetKValue): # staff action
    def test_should_not_query_anon(self):
        bad_field = {"qqquery": "1"}
        bad_value_non_integer = {"query": "vea"}
        bad_value_non_valid = {"query": "4"}

        response = self.client.post(reverse("query_results"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        self.two_fa_customer_1()
        response = self.client.post(reverse("query_results"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.two_fa_staff5()
        response = self.client.post(reverse("query_results"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff4()
        response = self.client.post(reverse("query_results"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("query_results"), bad_value_non_integer, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("query_results"), bad_value_non_valid, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_query_anon(self):
        self.set_k_value()
        sample_set_k = {"query": "1"}
        self.two_fa_staff4()
        response = self.client.post(reverse("query_results"), sample_set_k, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestGetAnonData(TestQueryAnon): # staff action
    def test_should_not_query_anon(self):
        bad_field = {"qqquery": "1"}
        bad_value_non_integer = {"query": "vea"}
        bad_value_non_valid = {"query": "4"}

        response = self.client.post(reverse("get_anon_data"), bad_field)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        self.two_fa_customer_1()
        response = self.client.post(reverse("get_anon_data"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.two_fa_staff4()
        response = self.client.post(reverse("get_anon_data"), bad_field, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("get_anon_data"), bad_value_non_integer, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("get_anon_data"), bad_value_non_valid, **self.header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_query_anon(self):
        self.set_k_value()
        sample_set_k = {"query": "1"}

        self.two_fa_staff4()
        response = self.client.post(reverse("get_anon_data"), sample_set_k, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        self.two_fa_staff5()
        response = self.client.post(reverse("get_anon_data"), sample_set_k, **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
