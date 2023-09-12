from django.contrib.auth import login

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from knox.views import LoginView as KnoxLoginView
from user.serializers import UserRegisterSerializer, LoginSerializer

staff_type = {'type': 'S'}

# Create your views here.
# class StaffRegistrationView(APIView):
#     def post(self, request):        
#         serializer = UserRegisterSerializer(data=request.data, context=staff_type)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class StaffLoginView(KnoxLoginView):
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context=staff_type)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            response = super().post(request, format=None)

            # Delete all existing tokens for that user
            if request.user.is_authenticated:
                request.user.auth_token_set.all().delete()

            return Response(response.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)