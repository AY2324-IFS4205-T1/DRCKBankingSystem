from django.contrib.auth import login

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from knox.views import LoginView as KnoxLoginView
from user.serializers import UserSerializer, LoginSerializer

customer_type = {'type': 'c'}

# Create your views here.
class RegistrationView(APIView):
    def post(self, request):        
        serializer = UserSerializer(data=request.data, context=customer_type)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(KnoxLoginView):
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context=customer_type)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            response = super().post(request, format=None)

            return Response(response.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)