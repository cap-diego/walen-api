# From django
from django.contrib.auth import get_user_model

# From drf
from rest_framework import serializers

# From w
from purchases.models import Purchase
from users.serializers import AddressSerializer
from carts.models import Cart

class PurchaseGETSerializer(serializers.ModelSerializer):
    shipment_area_center = AddressSerializer()
    status = serializers.CharField(source="get_status_display")
    class Meta:
        model = Purchase
        fields = '__all__'

class PurchasePOSTSerializer(serializers.Serializer):
    
    cart_id = serializers.PrimaryKeyRelatedField(
            queryset=Cart.objects.all())
    clients_target = serializers.IntegerField()

    
