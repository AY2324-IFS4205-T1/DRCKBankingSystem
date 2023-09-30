from django.contrib.auth import login
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from staff.permissions import IsStaff, IsTicketReviewer
from staff.serializers import (ApproveSerializer, GetClosedTicketsSerializer,
                               GetOpenTicketsSerializer, RejectSerializer,
                               StaffSerializer, TicketDetailsSerializer)
from user.authentication import TokenAndTwoFactorAuthentication
from user.models import User
from user.serializers import LoginSerializer, UserRegisterSerializer


# Create your views here.
class StaffRegistrationView(APIView):
    """
    username: staff1
    email: staff1@gmail.com
    phone_no: 12345678
    password: G00dP@55word
    first_name: first
    last_name: last
    birth_date: 1990-01-01
    title: Ticket Reviewer
    gender: Male
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
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = self.serializer_class(User.user_type.STAFF, data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            response = super().post(request, format=None)            
            return Response(response.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class StaffWelcomeView(APIView):
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
    permission_classes = (permissions.IsAuthenticated, IsStaff, IsTicketReviewer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)

    def get(self, request):
        serializer = GetOpenTicketsSerializer().get_open_tickets_list()
        return Response({"tickets": serializer}, status=status.HTTP_200_OK)


class GetClosedTicketsView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsStaff, IsTicketReviewer,)
    authentication_classes = (TokenAndTwoFactorAuthentication,)

    def get(self, request):
        serializer = GetClosedTicketsSerializer(request.user).get_closed_tickets_list()
        return Response({"tickets": serializer}, status=status.HTTP_200_OK)


class StaffTicketView(APIView):
    '''
    ticket_id: 
    '''
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
    """
    ticket_id: d1fa1bcc-c558-4f45-86eb-fef2caff0ecb
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
    """
    ticket_id: b69eed6a-d494-48c1-84e7-6b53ed3ab5db
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
