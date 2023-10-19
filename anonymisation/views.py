from django.http import FileResponse, HttpResponse
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from anonymisation.anonymise.overall import TooShortException
from anonymisation.permissions import IsAnonymiser, IsResearcher, IsResearcherOrAnonymiser
from anonymisation.serializers import (QueryAnonSerializer,
                                       SetKValueSerializer,
                                       ViewAnonStatsSerializer)
from anonymisation.wrapper import generate_statistics
from staff.permissions import IsStaff
from user.authentication import TokenAndTwoFactorAuthentication


class CalculateAnonView(APIView):
    """Get request
    """

    permission_classes = (permissions.IsAuthenticated, IsStaff, IsAnonymiser)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "sensitive_request"

    def get(self, request):
        try:
            generate_statistics()
            return Response(status=status.HTTP_200_OK)
        except TooShortException as error:
            return Response(error.__str__(), status=status.HTTP_200_OK)
        except Exception as error:
            return Response(error.__str__(), status=status.HTTP_400_BAD_REQUEST)


class ViewAnonStatsView(APIView):
    """Get request

    Returns:
        FileReponse
    """

    permission_classes = (permissions.IsAuthenticated, IsStaff, IsAnonymiser)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "non_sensitive_request"

    def get(self, request):
        graph = ViewAnonStatsSerializer().get_graph()
        return FileResponse(graph, content_type="image/png")


class SetKValueView(APIView):
    """Post request

    Args:
        k_value: integer

    Returns:
        success: "K-value has been set."
    """

    permission_classes = (permissions.IsAuthenticated, IsStaff, IsAnonymiser)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "sensitive_request"

    def post(self, request):
        serialiser = SetKValueSerializer(request.data, data=request.data)
        if serialiser.is_valid():
            serialiser.set_k()
            return Response({"success": "K-value has been set."}, status=status.HTTP_200_OK)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)


class QueryAnonView(APIView):
    """Post request

    Args:
        query: integer

    Returns:
        utility: utility of dataset for query
        results: query results

    Sample for query 1:
    {
    "utility": 0.0,
    "results":
        {
            "first_average": 0.0,
            "second_average": 0.0,
            "third_average": 0.0,
            "fourth_average": 0.0,
            "fifth_average": 0.0
        }
    }

    Sample for query 2:
    {
    "utility": 0.0,
    "results":
        {
            "first_balance_average": 0.0,
            "second_balance_average": 0.0,
            "third_balance_average": 0.0
        }
    }
    """

    permission_classes = (permissions.IsAuthenticated, IsStaff, IsResearcher)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "non_sensitive_request"

    def post(self, request):
        serialiser = QueryAnonSerializer(request.data, data=request.data)
        if serialiser.is_valid():
            response = serialiser.get_query_results()
            return Response(response, status=status.HTTP_200_OK)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)


class GetAnonDataView(APIView):
    """Post request

    Args:
        query: integer

    Returns:
        CSV file with anonymous data
    """

    permission_classes = (permissions.IsAuthenticated, IsStaff, IsResearcherOrAnonymiser)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "sensitive_request"

    def post(self, request):
        serialiser = QueryAnonSerializer(request.data, data=request.data)
        if serialiser.is_valid():
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": 'attachment; filename="drck_banking_anon_data.csv"'},
            )
            response = serialiser.get_anon_data(response)
            return response
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)
