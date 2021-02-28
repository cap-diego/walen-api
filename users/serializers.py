# From django
from django.contrib.auth import get_user_model

# From drf
from rest_framework import serializers

# From w
from users.models import Address, AddressGeoCodingResult

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'last_name', 'date_joined', 'last_login']

class AddressSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Address
        fields = '__all__'

class AddressGeoCodingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressGeoCodingResult
        fields = '__all__'

