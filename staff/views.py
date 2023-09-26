from django.contrib.auth import login
from knox.auth import TokenAuthentication
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from staff.serializers import (ApproveSerializer, GetClosedTicketsSerializer,
                               GetOpenTicketsSerializer, RejectSerializer,
                               StaffSerializer, TicketDetailsSerializer)
from staff.models import Tickets, RequestCloseAccount, RequestOpenAccount
from customer.models import Customer
from user.models import User
from user.serializers import LoginSerializer, UserRegisterSerializer

staff_type = {"type": "Staff"}


# Create your views here.
class StaffRegistrationView(APIView):
    """
    username: staff
    email: test@gmail.com
    phone_no: 12345678
    password: testpassword
    first_name: first
    last_name: last
    birth_date: 2023-01-01
    title: employee
    gender: M
    """

    def post(self, request):
        user_serializer = UserRegisterSerializer(data=request.data, context=staff_type)
        staff_serializer = StaffSerializer(data=request.data)

        if user_serializer.is_valid():
            if staff_serializer.is_valid():
                new_user = user_serializer.save(type=User.user_type.STAFF)
                staff_serializer.save(user=new_user)
                return Response(status=status.HTTP_201_CREATED)
            return Response(staff_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffLoginView(KnoxLoginView):
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context=staff_type)

        if serializer.is_valid():
            user = serializer.validated_data["user"]  # type: ignore
            login(request, user)
            response = super().post(request, format=None)

            response.data["type"] = staff_type["type"] 

            return Response(response.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class StaffWelcomeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    # Displays the user's first name, last name, last login in Dashboard
    def get(self, request):
        data = {
            'last_login': request.user.last_login,
            'first_name': request.user.staff.first_name,
            'last_name': request.user.staff.last_name
        }

        return Response(data, status=status.HTTP_200_OK)

class GetOpenTicketsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        serializer = GetOpenTicketsSerializer().get_open_tickets_list()
        return Response({"tickets": serializer}, status=status.HTTP_200_OK)


class GetClosedTicketsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        serializer = GetClosedTicketsSerializer(request.user).get_closed_tickets_list()
        return Response({"tickets": serializer}, status=status.HTTP_200_OK)

# class TicketDetailsView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     authentication_classes = (TokenAuthentication,)

#     def post(self, request):
#         serializer = TicketDetailsSerializer(request.user, request.data, data=request.data)
#         if serializer.is_valid():
#             serializer = serializer.get_ticket_details()
#             return Response(serializer, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StaffTicketView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    # Get ticket of a customer
    def get(self, request, ticket_id):
        # Retrieve ticket info
        ticket = Tickets.objects.filter(ticket=ticket_id).values()[0]
        value = None
        if ticket['ticket_type'] == Tickets.TicketType.OPEN_ACCOUNT:
            value = RequestOpenAccount.objects.filter(ticket_id=ticket_id).values('account_type_id__name')[0]['account_type_id__name']
            ticket['value'] = value
        elif ticket['ticket_type'] == Tickets.TicketType.CLOSE_ACCOUNT:
            value = RequestCloseAccount.objects.get(ticket_id=ticket_id).account_id.account
            ticket['value'] = value

        # Retrieve cust info
        customer = Customer.objects.filter(user_id=ticket['created_by_id']).values()[0]

        # Retrieve email and phone number of user
        user = User.objects.get(pk=ticket['created_by_id'])

        customer['email']=user.email
        customer['phone_no']=user.phone_no

        del customer['identity_no']
        del customer['user_id']
        del ticket['created_by_id']

        return Response({'ticket': ticket, 'customer': customer}, status=status.HTTP_200_OK)
    
class ApproveView(APIView):
    """
    ticket_id: d1fa1bcc-c558-4f45-86eb-fef2caff0ecb
    """

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, ticket_id):
        serializer = ApproveSerializer(request.user, request.data, ticket_id, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RejectView(APIView):
    """
    ticket_id: b69eed6a-d494-48c1-84e7-6b53ed3ab5db
    """

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, ticket_id):
        serializer = RejectSerializer(request.user, request.data, ticket_id, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)