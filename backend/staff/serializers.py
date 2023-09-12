from rest_framework import serializers
from .models import Staff

class StaffSerializer(serializers.ModelSerializer):
    user = serializers.Field(required=False)

    class Meta:
        model = Staff
        fields = ('user', 'department', 'first_name', 'last_name', 'title', 'birth_date', 'gender')