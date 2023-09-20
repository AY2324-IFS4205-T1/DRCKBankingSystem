from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from knox.auth import TokenAuthentication

# Create your views here.
class AuthenticationCheckView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, _):
        return Response(status=status.HTTP_200_OK)