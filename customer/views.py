from django.contrib.auth import login

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from knox.views import LoginView as KnoxLoginView
from user.serializers import UserRegisterSerializer, LoginSerializer

customer_type = {'type': 'C'}

# In body (form data),
# username: test
# email: test@gmail.com
# phone_no: 12345678
# password: password
# first_name: first
# last_name: last
# birth_date: 2023-01-01
# identity_no: S1234567B
# address: jurong
# nationality: africa
# gender: M
class CustomerRegistrationView(APIView):
    def post(self, request):      
        serializer = UserRegisterSerializer(data=request.data, context=customer_type)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# In body (form data),
# username: test
# password: password
# Please keep the token for logout
class CustomerLoginView(KnoxLoginView):
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