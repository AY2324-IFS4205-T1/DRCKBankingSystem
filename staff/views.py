from django.contrib.auth import login
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from staff.permissions import IsResearcher, IsStaff, IsTicketReviewer
from staff.serializers import (AnonymisationSerializer, ApproveSerializer,
                               GetClosedTicketsSerializer,
                               GetOpenTicketsSerializer, RejectSerializer,
                               StaffSerializer, TicketDetailsSerializer)
from user.authentication import TokenAndTwoFactorAuthentication
from user.models import User
from user.serializers import LoginSerializer, UserRegisterSerializer


# Create your views here.
class StaffRegistrationView(APIView):
    """TO BE DELETED IN PRODUCTION
    Post request

    Args:
        username: staff1
        email: staff1@gmail.com
        phone_no: 12345678
        password: G00dP@55word
        first_name: first
        last_name: last
        birth_date: 1999-01-01
        title: string, options are ["Ticket Reviewer", "Security Engineer", "Researcher"]
        gender: string, options are ["Male", "Female", "Others"]

    Returns:
        success: "Staff is successfully registered."

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
        user_serializer = UserRegisterSerializer(User.user_type.STAFF, data=request.data)

        if user_serializer.is_valid():
            user = user_serializer.save(type=User.user_type.STAFF)
            staff_serializer = StaffSerializer(data=request.data, user=user)
            if staff_serializer.is_valid():
                staff_serializer.save(user=user)
                return Response({"success": "Staff is successfully registered."}, status=status.HTTP_201_CREATED)
            else:
                user.delete()
                return Response(staff_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffLoginView(KnoxLoginView):
    """Post request

    Args:        
        username: staff1
        password: G00dP@55word

    Returns:
        _type_: _description_
    """
    permission_classes = (permissions.AllowAny,)
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(User.user_type.STAFF, data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            return super().post(request, format=None)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class StaffWelcomeView(APIView):
    """Get request

    Returns:
        last_login: timestamp
        first_name: string,
        last_name: string,
    """
    permission_classes = (permissions.IsAuthenticated, IsStaff)
    authentication_classes = (TokenAndTwoFactorAuthentication,)

    # Displays the user's first name, last name, last login in Dashboard
    def get(self, request):
        data = {
            'last_login': request.user.last_login,
            'first_name': request.user.staff.first_name,
            'last_name': request.user.staff.last_name
        }

        return Response(data, status=status.HTTP_200_OK)

class GetOpenTicketsView(APIView):
    """Get request

    Returns:
        tickets: list of opened tickets
    """
    permission_classes = (permissions.IsAuthenticated, IsStaff, IsTicketReviewer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)

    def get(self, request):
        serializer = GetOpenTicketsSerializer().get_open_tickets_list()
        return Response({"tickets": serializer}, status=status.HTTP_200_OK)


class GetClosedTicketsView(APIView):
    """Get request

    Returns:
        tickets: list of closed tickets
    """
    permission_classes = (permissions.IsAuthenticated, IsStaff, IsTicketReviewer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)

    def get(self, request):
        serializer = GetClosedTicketsSerializer(request.user).get_closed_tickets_list()
        return Response({"tickets": serializer}, status=status.HTTP_200_OK)


class StaffTicketView(APIView):
    """Post request

    Args:
        ticket_id: ticket_id

    Returns:
        ticket: ticket, ticket_type, status, created_date, closed_date, value
        customer: first_name, last_name, birth_date, citizenship, email, phone_no
        accounts: list of accounts (account, type, balance, status, date_created) owned by customer
    """
    permission_classes = (permissions.IsAuthenticated, IsStaff, IsTicketReviewer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "non_sensitive_request"

    def post(self, request):
        serializer = TicketDetailsSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer = serializer.get_ticket_details()
            return Response(serializer, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApproveView(APIView):
    """Post request

    Args:
        ticket_id: d1fa1bcc-c558-4f45-86eb-fef2caff0ecb

    Returns:
        success: "Ticket has been approved."
    """
    permission_classes = (permissions.IsAuthenticated, IsStaff, IsTicketReviewer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "sensitive_request"

    def post(self, request):
        serializer = ApproveSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Ticket has been approved."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RejectView(APIView):
    """Post request

    Args:
        ticket_id: d1fa1bcc-c558-4f45-86eb-fef2caff0ecb

    Returns:
        success: "Ticket has been rejected."
    """
    permission_classes = (permissions.IsAuthenticated, IsStaff, IsTicketReviewer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)
    throttle_scope = "sensitive_request"

    def post(self, request):
        serializer = RejectSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Ticket has been rejected."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

      
class AnonymisationView(APIView):
    """Post request

    Args:
        k_value: number
        query: number

    Returns:
        data: anonymised data
    """
    permission_classes = (permissions.IsAuthenticated, IsStaff, IsResearcher)
    authentication_classes = (TokenAndTwoFactorAuthentication,)

    def post(self, request):
        serializer = AnonymisationSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer = serializer.get_anonymised_data()
            return Response(serializer, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
