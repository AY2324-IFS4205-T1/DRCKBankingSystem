from django.http import FileResponse
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from anonymisation.anonymise.overall import TooShortException

from anonymisation.permissions import IsAnonymiser, IsResearcher
from anonymisation.serializers import QueryAnonSerializer, SetKValueSerializer, ViewAnonStatsSerializer
from anonymisation.wrapper import generate_statistics
from staff.permissions import IsStaff
from user.authentication import TokenAndTwoFactorAuthentication


class CalculateAnonView(APIView):
    """Get request
    TODO: @rebecca, API works but generate_statistics() does not work
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
    TODO: @rebecca, API works but generate_statistics() does not work

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
        anon_data: dict of the anonymous data set
        utility: utility of dataset for query
        results: query results
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
