from django.contrib.auth import login

from rest_framework import status, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from knox.views import LoginView as KnoxLoginView
from customer.serializers import ApplySerializer, GetAccountTypesSerializer, GetBalanceSerializer
from user.serializers import UserRegisterSerializer, LoginSerializer

customer_type = {'type': 'C'}

class CustomerRegistrationView(APIView):
    '''
    username: test
    email: test@gmail.com
    phone_no: 12345678
    password: testpassword
    first_name: first
    last_name: last
    birth_date: 2023-01-01
    identity_no: S1234567B
    address: jurong
    nationality: africa
    gender: m
    '''
    def post(self, request):        
        serializer = UserRegisterSerializer(data=request.data, context=customer_type)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerLoginView(KnoxLoginView):
    '''
    username: test
    password: password
    Please keep the token for logout
    '''
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context=customer_type)
        
        if serializer.is_valid():
            user = serializer.validated_data['user'] # type: ignore
            login(request, user)
            response = super().post(request, format=None)

            return Response(response.data, status=status.HTTP_201_CREATED)
    

class GetAccountTypesView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    
    def get(self, request):
        serializer = GetAccountTypesSerializer(request.user).get_account_type_list()
        return Response({'account_types': serializer}, status=status.HTTP_200_OK)


class ApplyView(APIView):
    '''
    account_type: savings / credit card / investments
    '''
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    
    def post(self, request):
        serializer = ApplySerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetBalanceView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    
    def get(self, request):
        serializer = GetBalanceSerializer(request.user).get_balance()
        return Response({'balance': serializer}, status=status.HTTP_200_OK)

