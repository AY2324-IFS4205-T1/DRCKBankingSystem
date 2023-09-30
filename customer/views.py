from django.contrib.auth import login
from django.db.models import F
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from customer.models import Accounts, AccountTypes
from customer.permissions import IsCustomer
from customer.serializers import (CreateTicketSerializer, CustomerSerializer,
                                  DepositSerializer, GetTicketsSerializer,
                                  TransactionsSerializer, TransferSerializer,
                                  WithdrawSerializer)
from user.authentication import TokenAndTwoFactorAuthentication
from user.models import User
from user.serializers import LoginSerializer, UserRegisterSerializer


class CustomerRegistrationView(APIView):
    """
    username: test1
    email: test1@gmail.com
    phone_no: 12345678
    password: G00dP@55word
    first_name: first
    last_name: last
    birth_date: 1999-01-01
    identity_no: S9934567B
    address: jurong
    postal_code: 123456
    citizenship: Singaporean Citizen
    gender: Male
    """

    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        user_serializer = UserRegisterSerializer(
            User.user_type.CUSTOMER, data=request.data
        )

        if user_serializer.is_valid():
            user = user_serializer.save(type=User.user_type.CUSTOMER)
            customer_serializer = CustomerSerializer(data=request.data, user=user)
            if customer_serializer.is_valid():
                customer_serializer.save(user=user)
                return Response({"success": "Customer has been successfully registered."}, status=status.HTTP_201_CREATED)
            else:
                user.delete()
                return Response(customer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerLoginView(KnoxLoginView):
    """
    username: test1
    password: G00dP@55word
    Please keep the token for logout
    """
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = self.serializer_class(User.user_type.CUSTOMER, data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            response = super().post(request, format=None)
            return Response(response.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerWelcomeView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)

    # Displays the user's first name, last name, last login in Dashboard
    def get(self, request):
        data = {
            "last_login": request.user.last_login,
            "first_name": request.user.customer.first_name,
            "last_name": request.user.customer.last_name,
        }

        return Response(data, status=status.HTTP_200_OK)


class AccountTypesView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "non_sensitive_request"

    def get(self, request):
        account_types = AccountTypes.objects.values()
        return Response({"account_types": account_types}, status=status.HTTP_200_OK)


class AccountsView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "non_sensitive_request"

    # Get all accounts of the user
    def get(self, request):
        accounts = Accounts.objects.filter(user_id__user=self.request.user, status=Accounts.AccountStatus.ACTIVE).values("account", "balance", acct_type=F("type_id__name"))
        return Response({"accounts": accounts}, status=status.HTTP_200_OK)


class TransactionsView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)

    # Get all transactions of an account
    def post(self, request):
        # Check if the account belong to the user
        serialiser = TransactionsSerializer(request.user, request.data, data=request.data)
        if serialiser.is_valid():
            transactions = serialiser.get_transactions()
            return Response({"transactions": transactions}, status=status.HTTP_200_OK)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerTicketsView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsCustomer)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "non_sensitive_request"

    def get(self, request):
        serializer = GetTicketsSerializer(request.user).get_customer_tickets()
        return Response({"tickets": serializer}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CreateTicketSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Ticket has been created."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepositView(APIView):
    """
    account_id: 89c46857-d9f7-4f5d-b221-0936b78e8b7b
    amount: 50
    """
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "sensitive_request"

    def post(self, request):
        serializer = DepositSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            new_balance = serializer.save()
            return Response({"new_balance": new_balance}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WithdrawView(APIView):
    """
    account_id: 89c46857-d9f7-4f5d-b221-0936b78e8b7b
    amount: 50
    """

    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "sensitive_request"

    def post(self, request):
        serializer = WithdrawSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            new_balance = serializer.save()
            return Response({"new_balance": new_balance}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransferView(APIView):
    """
    sender_id: 89c46857-d9f7-4f5d-b221-0936b78e8b7b
    recipient_id: b7ee7413-3dbd-4fde-96b8-658dfc02b62f
    amount: 50
    description: string
    """

    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "sensitive_request"

    def post(self, request):
        serializer = TransferSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Transfer was successfully made."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
