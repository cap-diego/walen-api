# From django
from django.contrib.auth import get_user_model

# From drf
from rest_framework import serializers

# From w
from purchases.models import Purchase
from users.serializers import AddressSerializer
from carts.models import Cart
from carts.serializers import CartSerializer

class PurchaseGETSerializer(serializers.ModelSerializer):
    shipment_area_center = AddressSerializer()
    cart = CartSerializer()
    status = serializers.CharField(source="get_status_display")
    clients_left = serializers.ReadOnlyField()
    clients_target_reached = serializers.ReadOnlyField()
    cart_price = serializers.ReadOnlyField()
    amount_to_pay = serializers.ReadOnlyField()
    shipment_area_radius = serializers.ReadOnlyField()

    class Meta:
        model = Purchase
        fields = '__all__'

class PurchasePOSTSerializer(serializers.Serializer):
    
    cart_id = serializers.PrimaryKeyRelatedField(
            queryset=Cart.objects.all())
    clients_target = serializers.IntegerField()

    
