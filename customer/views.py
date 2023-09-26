from django.contrib.auth import login
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from customer.permissions import IsCustomer
from customer.serializers import (CreateTicketSerializer, CustomerSerializer,
                                  DepositSerializer,
                                  GetTicketsSerializer, TransferSerializer,
                                  WithdrawSerializer)
from user.authentication import TokenAndTwoFactorAuthentication
from user.models import User
from staff.models import Tickets, RequestOpenAccount, RequestCloseAccount
from user.serializers import LoginSerializer, UserRegisterSerializer
from customer.models import AccountTypes, Accounts, Transactions

from django.db.models import F, Q


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

            response.data["type"] = User.user_type.CUSTOMER
            
            return Response(response.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomerWelcomeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAndTwoFactorAuthentication, IsCustomer,)

    # Displays the user's first name, last name, last login in Dashboard
    def get(self, request):
        data = {
            'last_login': request.user.last_login,
            'first_name': request.user.customer.first_name,
            'last_name': request.user.customer.last_name
        }

        return Response(data, status=status.HTTP_200_OK)

class AccountTypesView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "non_sensitive_request"

    def get(self, request):
        account_types = AccountTypes.objects.values()
        return Response({'account_types': account_types}, status=status.HTTP_200_OK)

class AccountsView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "non_sensitive_request"
    
    # Get all accounts of the user
    def get(self, request):
        accounts = Accounts.objects.filter(user_id__user=self.request.user, status=Accounts.AccountStatus.ACTIVE).values("account", "balance", acct_type=F("type_id__name"))
        return Response({'accounts': accounts}, status=status.HTTP_200_OK)
    
class TransactionsView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)

    # Get all transactions of an account
    def get(self, request, acct_id):
        # Check if the account belong to the user
        has_acct = Accounts.objects.filter(account=acct_id, user_id=request.user.id).exists()
        if has_acct is True:
            transactions = Transactions.objects.filter(Q(sender_id=acct_id)|Q(recipient_id=acct_id)).values()
            return Response({'transactions': transactions}, status=status.HTTP_200_OK)

# class ApplyView(APIView):
#     '''
#     account_type: Savings / Credit Card / Investments
#     '''
#     permission_classes = (permissions.IsAuthenticated,)
#     authentication_classes = (TokenAndTwoFactorAuthentication,)
    
#     def post(self, request):
#         serializer = ApplySerializer(request.user, request.data, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerTicketsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "non_sensitive_request"
    
    def get(self, request):
        try:
            serializer = GetTicketsSerializer(request.user).get_customer_tickets()
            return Response({'tickets': serializer}, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        serializer = CreateTicketSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerTicketView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "non_sensitive_request"

    # Get ticket of a customer
    def get(self, request, ticket_id):
        ticket = Tickets.objects.filter(ticket=ticket_id, created_by=request.user.id).values()[0]
        if ticket['ticket_type'] == Tickets.TicketType.OPEN_ACCOUNT:
            value = RequestOpenAccount.objects.filter(ticket_id=ticket_id).values('account_type_id__name')[0]['account_type_id__name']
            ticket['value'] = value
        elif ticket['ticket_type'] == Tickets.TicketType.CLOSE_ACCOUNT:
            value = RequestCloseAccount.objects.get(ticket_id=ticket_id).account_id.account
            ticket['value'] = value
        return Response({'ticket': ticket}, status=status.HTTP_200_OK)
        

class DepositView(APIView):
    '''
    account_id: 89c46857-d9f7-4f5d-b221-0936b78e8b7b
    amount: 50
    '''
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "sensitive_request"
    
    def post(self, request):
        # Added description to ATM Deposit
        request.data["description"] = "ATM Deposit"
        serializer = DepositSerializer(request.user, request.data, data=request.data)

        if serializer.is_valid():
            serializer.save()
            # serialize.instance returns the defined new_balance set in serializer
            return Response(serializer.instance, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WithdrawView(APIView):
    '''
    account_id: 89c46857-d9f7-4f5d-b221-0936b78e8b7b
    amount: 50
    '''
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "sensitive_request"
    
    def post(self, request):
        # Added description to ATM Withdraw
        request.data["description"] = "ATM Withdraw"
        serializer = WithdrawSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.instance, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransferView(APIView):
    '''
    sender_id: 89c46857-d9f7-4f5d-b221-0936b78e8b7b
    recipient_id: b7ee7413-3dbd-4fde-96b8-658dfc02b62f
    amount: 50
    description: string
    '''
    permission_classes = (permissions.IsAuthenticated, IsCustomer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "sensitive_request"
    
    def post(self, request):
        serializer = TransferSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
