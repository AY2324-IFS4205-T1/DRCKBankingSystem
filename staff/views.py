from django.contrib.auth import login

from rest_framework import status, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from knox.views import LoginView as KnoxLoginView
from staff.serializers import ApproveSerializer, GetClosedTicketsSerializer, GetOpenTicketsSerializer, RejectSerializer
from user.serializers import UserRegisterSerializer, LoginSerializer

staff_type = {'type': 'S'}

# Create your views here.
class StaffRegistrationView(APIView):
    '''
    username: staff
    email: test@gmail.com
    phone_no: 12345678
    password: testpassword
    first_name: first
    last_name: last
    birth_date: 2023-01-01
    title: employee
    gender: M
    '''
    def post(self, request):        
        serializer = UserRegisterSerializer(data=request.data, context=staff_type)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

      
class StaffLoginView(KnoxLoginView):
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context=staff_type)
        
        if serializer.is_valid():
            user = serializer.validated_data['user'] # type: ignore
            login(request, user)
            response = super().post(request, format=None)

            # Delete all existing tokens for that user
            if request.user.is_authenticated:
                request.user.auth_token_set.all().delete()

            return Response(response.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApproveView(APIView):
    '''
    ticket_id: d1fa1bcc-c558-4f45-86eb-fef2caff0ecb
    '''
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    
    def post(self, request):
        serializer = ApproveSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RejectView(APIView):
    '''
    ticket_id: b69eed6a-d494-48c1-84e7-6b53ed3ab5db
    '''
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    
    def post(self, request):
        serializer = RejectSerializer(request.user, request.data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GetOpenTicketsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    
    def get(self, request):
        serializer = GetOpenTicketsSerializer().get_open_tickets_list()
        return Response({'open_tickets': serializer}, status=status.HTTP_200_OK)


class GetClosedTicketsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    
    def get(self, request):
        serializer = GetClosedTicketsSerializer(request.user).get_closed_tickets_list()
        return Response({'open_tickets': serializer}, status=status.HTTP_200_OK)
