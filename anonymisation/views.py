from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from anonymisation.permissions import IsAnonymiser, IsResearcher
from staff.permissions import IsStaff
from user.authentication import TokenAndTwoFactorAuthentication

from anonymisation.serializers import AnonymisationSerializer, QuerySerializer


class AnonymisationView(APIView):
    """Post request

    Args:
        k_value: number

    Returns:
        data: anonymised data
    """
    permission_classes = (permissions.IsAuthenticated, IsStaff, IsAnonymiser)
    authentication_classes = (TokenAndTwoFactorAuthentication,)

    def post(self, request):
        serializer = AnonymisationSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer = serializer.get_anonymised_data()
            return Response(serializer, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QueryView(APIView):
    """Post request

    Args:
        anon_dict: anonymised_data

    Returns:
        data: anonymised data
    """
    permission_classes = (permissions.IsAuthenticated, IsStaff, IsResearcher)
    authentication_classes = (TokenAndTwoFactorAuthentication,)

    def post(self, request):
        serializer = QuerySerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer = serializer.get_query_result()
            return Response(serializer, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

'''
calculate_anon --> by officer
  - takes in query number and returns a statistical graph for officer
  - i will call your generate_statistics

view_statistics --> by officer
  - i will retrieve data (k, query number, infoloss, utility, result) saved above, convert into a graph, send to user

set_k_value --> by officer
  - takes in k_value
  - i will call your generate_k_anon to obtain the k-anon-data
  - i will pass k-anon-data into your save_anon

query_anon_data --> by researcher
  - takes in query number
  - i will grab data from database and return to researcher
  - i will grab (results, utility) from database based on (query number, set_k_value)
'''