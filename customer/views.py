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
from log.logging import ConflictOfInterestLogger, LoginLogger
from user.authentication import TokenAndTwoFactorAuthentication
from user.models import User
from user.serializers import LoginSerializer, UserRegisterSerializer
from django.views.decorators.csrf import ensure_csrf_cookie

class CustomerRegistrationView(APIView):
    """Post request

    Args:
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
        citizenship: string, options are ["Singaporean Citizen", "Singaporean PR", "Non-Singaporean"]
        gender: string, options are ["Male", "Female", "Others"]

    Returns:
        success: "Customer has been successfully registered."

    password:
        - must be at least maximum 0.7 similarity to username and email
        - has a minimum length of 8 characters
        - cannot be a common password
        - cannot be fully numeric
        - has a maximum length of 64 characters
        - must have at least 2 uppercase characters
        - must have at least 2 lowercase characters
        - must have at least 1 numeric character
        - must have at least 1 special character

    identity_no needs to be valid with respect to citizenship and birth_date
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


@ensure_csrf_cookie
class CustomerLoginView(KnoxLoginView):
    """Post request

    Args:        
        username: test1
        password: G00dP@55word

    Returns:
        _type_: _description_
    """
    permission_classes = (permissions.AllowAny,)
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(User.user_type.CUSTOMER, data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            response = super().post(request, format=None)
            LoginLogger(User.user_type.CUSTOMER, request, response, user)
            return response
        LoginLogger(User.user_type.CUSTOMER, request)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerWelcomeView(APIView):
    """Get request

    Returns:
        last_login: timestamp
        first_name: string,
        last_name: string,
    """
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "non_sensitive_request"

    def get(self, request):
        data = {
            "last_login": request.user.last_login,
            "first_name": request.user.customer.first_name,
            "last_name": request.user.customer.last_name,
        }
        return Response(data, status=status.HTTP_200_OK)


class AccountTypesView(APIView):
    """Get request

    Returns:
        account_types: list of account_types (string)
    """
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "non_sensitive_request"

    def get(self, request):
        account_types = AccountTypes.objects.values()
        return Response({"account_types": account_types}, status=status.HTTP_200_OK)


class AccountsView(APIView):
    """Get request

    Returns:
        accounts: list of accounts (account, balance, acct_type)
    """
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "non_sensitive_request"

    # Get all accounts of the user
    def get(self, request):
        accounts = Accounts.objects.filter(user_id__user=self.request.user, status=Accounts.AccountStatus.ACTIVE).values("account", "balance", acct_type=F("type_id__name"))
        return Response({"accounts": accounts}, status=status.HTTP_200_OK)


class TransactionsView(APIView):
    """Post request

    Args:
        account_id: account_id

    Returns:
        transactions: list of transactions
    """
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
    """Get request

    Returns:
        tickets: list of tickets ("ticket", "ticket_type", "status", "created_date", "closed_date") opened by customer

        
    Post request

    Args:
        ticket_type: string, options are ["Opening Account", "Closing Account"]
        value: AccountType if opening account, account_id if closing account

    Returns:
        success: "Ticket has been created."
    """
    permission_classes = (permissions.IsAuthenticated, IsCustomer)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "non_sensitive_request"

    def get(self, request):
        serializer = GetTicketsSerializer(request.user).get_customer_tickets()
        return Response({"tickets": serializer}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CreateTicketSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            ticket = serializer.save()
            ConflictOfInterestLogger(request, ticket)
            return Response({"success": "Ticket has been created."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepositView(APIView):
    """Post request

    Args:
        account_id: account_id
        amount: number
        description: string

    Returns:
        new_balance: number
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
    """Post request

    Args:
        account_id: account_id
        amount: number
        description: string

    Returns:
        new_balance: number
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
    """Post request

    Args:
        sender_id: account_id
        recipient_id: account_id
        amount: number
        description: string

    Returns:
        transaction: transaction information
    """
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "sensitive_request"

    def post(self, request):
        serializer = TransferSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            transaction = serializer.get_transaction()
            return Response(transaction, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
