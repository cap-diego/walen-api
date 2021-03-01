# From django
from django.contrib.auth import get_user_model
from django.db import transaction

# From drf
from rest_framework import serializers
from rest_framework.exceptions import APIException

# From w
from users.models import Address, AddressGeoCodingResult, \
    Client

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
        geocoding_data = validated_data.pop('geocoding', None)
        addr_data = validated_data
        geocoding = None
        if geocoding_data:
            geocoding = self.create_geocoding_result(geocoding_data)
        addr = self.create_address(addr_data, geocoding)
        return addr

    def create_geocoding_result(self, data):
        try:
            return AddressGeoCodingResult.objects.create(
                **data
            )
        except Exception as err:
            raise APIException(err)


    def create_address(self, data, geo=None):
        try:
            return Address.objects.create(
                geocoding=geo,
                **data
            )
        except Exception as err:
            raise APIException(err)

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class ClientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Client
        fields = ['user', 'email']