from django.contrib.auth import login
from django.db import transaction
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from log.logging import ConflictOfInterestLogger, LoginLogger
from staff.permissions import IsStaff, IsTicketReviewer
from staff.serializers import (ApproveSerializer, GetClosedTicketsSerializer,
                               GetOpenTicketsSerializer, RejectSerializer,
                               TicketDetailsSerializer)
from user.authentication import TokenAndTwoFactorAuthentication
from user.models import User
from user.serializers import LoginSerializer


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

    @transaction.atomic
    def post(self, request):
        serializer = LoginSerializer(User.user_type.STAFF, data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            response = super().post(request, format=None)
            LoginLogger(User.user_type.STAFF, request, response, user)
            return response
        LoginLogger(User.user_type.STAFF, request)
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

    @transaction.atomic
    # Displays the user's first name, last name, last login in Dashboard
    def get(self, request):
        data = {
            "last_login": request.user.last_login,
            "first_name": request.user.staff.first_name,
            "last_name": request.user.staff.last_name,
        }

        return Response(data, status=status.HTTP_200_OK)


class GetOpenTicketsView(APIView):
    """Get request

    Returns:
        tickets: list of opened tickets
    """

    permission_classes = (permissions.IsAuthenticated, IsStaff, IsTicketReviewer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)

    @transaction.atomic
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

    @transaction.atomic
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

    @transaction.atomic
    def post(self, request):
        serializer = TicketDetailsSerializer(
            request.user, request.data, data=request.data
        )
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

    @transaction.atomic
    def post(self, request):
        serializer = ApproveSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            ticket = serializer.save()
            ConflictOfInterestLogger(request, ticket)
            return Response(
                {"success": "Ticket has been approved."}, status=status.HTTP_200_OK
            )
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

    @transaction.atomic
    def post(self, request):
        serializer = RejectSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": "Ticket has been rejected."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

