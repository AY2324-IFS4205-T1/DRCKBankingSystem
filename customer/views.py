from django.contrib.auth import login
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from customer.serializers import (ApplySerializer, DepositSerializer,
                                  GetAccountTypesSerializer,
                                  GetBalanceSerializer, TransferSerializer,
                                  WithdrawSerializer)
from user.serializers import LoginSerializer, UserRegisterSerializer

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


class DepositView(APIView):
    '''
    account_id: 89c46857-d9f7-4f5d-b221-0936b78e8b7b
    amount: 50
    description: string
    '''
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    
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
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    
    def post(self, request):
        serializer = WithdrawSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransferView(APIView):
    '''
    sender_id: 
    recipient_id: b7ee7413-3dbd-4fde-96b8-658dfc02b62f
    amount: 50
    description: string
    '''
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    
    def post(self, request):
        serializer = TransferSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
