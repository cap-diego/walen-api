# From django
from django.contrib.auth import get_user_model
from django.db import transaction

# From drf
from rest_framework import serializers
from rest_framework.exceptions import APIException

# From w
from users.models import Address, AddressGeoCodingResult, \
    Client, create_address

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'last_name', 'date_joined', 'last_login']


class AddressGeoCodingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressGeoCodingResult
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):

    geocoding = AddressGeoCodingResultSerializer(allow_null=True)
    
    class Meta:
        model = Address
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        addr, err = create_address(validated_data)
        if err:
            raise APIException(err)
        return addr


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class ClientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Client
        fields = ['user', 'email']