from django.contrib.auth import login
from knox.auth import TokenAuthentication
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from customer.permissions import IsCustomer
from customer.serializers import (ApplySerializer, CustomerSerializer,
                                  DepositSerializer, GetAccountTypesSerializer,
                                  GetBalanceSerializer,
                                  GetCustomerTicketsSerializer,
                                  TransferSerializer, WithdrawSerializer)
from user.models import User
from user.serializers import LoginSerializer, UserRegisterSerializer


class CustomerRegistrationView(APIView):
    '''
    username: test
    email: test@gmail.com
    phone_no: 12345678
    password: G00dP@55word
    first_name: first
    last_name: last
    birth_date: 2023-01-01
    identity_no: S1234567B
    address: jurong
    postal_code: 123456
    citizenship: Singaporean Citizen
    gender: M
    '''

    throttle_classes = [AnonRateThrottle]

    def post(self, request):        
        user_serializer = UserRegisterSerializer(User.user_type.CUSTOMER, data=request.data)

        if user_serializer.is_valid():
            user = user_serializer.save(type=User.user_type.CUSTOMER)
            customer_serializer = CustomerSerializer(data=request.data, user=user)
            if customer_serializer.is_valid():
                customer_serializer.save(user=user)
                return Response(status=status.HTTP_201_CREATED)
            else:
                user.delete()
                return Response(customer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerLoginView(KnoxLoginView):
    '''
    username: test
    password: G00dP@55word
    Please keep the token for logout
    '''
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_classes = [AnonRateThrottle]
    
    def post(self, request):
        serializer = self.serializer_class(User.user_type.CUSTOMER, data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user'] # type: ignore
            login(request, user)
            response = super().post(request, format=None)
            return Response(response.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GetAccountTypesView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAuthentication,)
    throttle_scope = "non_sensitive_request"
    
    def get(self, request):
        serializer = GetAccountTypesSerializer(request.user).get_account_type_list()
        return Response({'account_types': serializer}, status=status.HTTP_200_OK)


class ApplyView(APIView):
    '''
    account_type: Savings / Credit Card / Investments
    '''
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAuthentication,)
    throttle_scope = "non_sensitive_request"
    
    def post(self, request):
        serializer = ApplySerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetCustomerTicketsView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAuthentication,)
    throttle_scope = "non_sensitive_request"
    
    def get(self, request):
        serializer = GetCustomerTicketsSerializer(request.user).get_customer_tickets()
        return Response({'balance': serializer}, status=status.HTTP_200_OK)


class GetBalanceView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAuthentication,)
    throttle_scope = "non_sensitive_request"
    
    def get(self, request):
        serializer = GetBalanceSerializer(request.user).get_balance()
        return Response({'balance': serializer}, status=status.HTTP_200_OK)


class DepositView(APIView):
    '''
    account_id: 89c46857-d9f7-4f5d-b221-0936b78e8b7b
    amount: 50
    description: string
    '''
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAuthentication,)
    throttle_scope = "sensitive_request"
    
    def post(self, request):
        serializer = DepositSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WithdrawView(APIView):
    '''
    account_id: 89c46857-d9f7-4f5d-b221-0936b78e8b7b
    amount: 50
    description: string
    '''
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAuthentication,)
    throttle_scope = "sensitive_request"
    
    def post(self, request):
        serializer = WithdrawSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransferView(APIView):
    '''
    sender_id: 89c46857-d9f7-4f5d-b221-0936b78e8b7b
    recipient_id: b7ee7413-3dbd-4fde-96b8-658dfc02b62f
    amount: 50
    description: string
    '''
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAuthentication,)
    throttle_scope = "sensitive_request"
    
    def post(self, request):
        serializer = TransferSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
