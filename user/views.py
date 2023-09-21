from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from knox.auth import TokenAuthentication

# Create your views here.
class AuthenticationTypeCheckView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    # Check if user is authenticated and see if the database user type and request user type matches
    def get(self, request):
        # Retrieves the request user type
        input_user_type = request.headers['Type']
        if input_user_type != self.request.user.type:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(status=status.HTTP_200_OK)