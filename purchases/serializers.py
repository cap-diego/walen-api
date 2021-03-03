# From django
from django.contrib.auth import get_user_model

# From drf
from rest_framework import serializers

# From w
from purchases.models import Purchase, IndividualPurchase, \
    Shipment, Payment, Coupon
from users.serializers import AddressSerializer, \
    ClientSerializer
from carts.models import Cart
from carts.serializers import CartSerializer
from purchases.constants import PAYMENT_VENDOR_CHOICES

class PurchaseGETSerializer(serializers.ModelSerializer):
    shipment_area_center = AddressSerializer()
    cart = CartSerializer()
    status = serializers.CharField(source="get_status_display")
    clients_left = serializers.ReadOnlyField()
    clients_target_reached = serializers.ReadOnlyField()
    cart_price = serializers.ReadOnlyField()
    amount = serializers.ReadOnlyField()
    shipment_area_radius = serializers.ReadOnlyField()
    expiration_date = serializers.ReadOnlyField()
    discount_amount = serializers.ReadOnlyField()
    class Meta:
        model = Purchase
        fields = '__all__'


class PurchasePOSTSerializer(serializers.Serializer):
    
    cart_id = serializers.PrimaryKeyRelatedField(
            queryset=Cart.objects.all())
    clients_target = serializers.IntegerField()

    
class IndividualPurchasePOSTSerializer(serializers.Serializer):

    client_email = serializers.EmailField()
    shipment_address = AddressSerializer()

class PaymentSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    individual_purchase_id = serializers.ReadOnlyField()
    amount_to_pay = serializers.ReadOnlyField()
    coupon = serializers.SerializerMethodField(method_name='get_coupon_display')

    def get_coupon_display(self, obj):
        if obj.coupon:
            return '{}'.format(obj.coupon)
        return 'sin coupon'

    class Meta:
        model = Payment
        fields = '__all__'

class ShipmentSerializer(serializers.ModelSerializer):
    shipment_address = AddressSerializer()
    status = serializers.CharField(source='get_status_display')
    individual_purchase_id = serializers.ReadOnlyField()
    class Meta:
        model = Shipment
        fields = '__all__'

class IndividualPurchaseGETSerializer(serializers.ModelSerializer):
    client = ClientSerializer()
    purchase = PurchaseGETSerializer()
    shipment = ShipmentSerializer()
    payment = PaymentSerializer()
    class Meta:
        model = IndividualPurchase
        fields = '__all__'

class IndividualPurchaseMiniGETSerializer(serializers.ModelSerializer):
    shipment_status = serializers.SerializerMethodField(method_name='get_shipment_status')
    payment_amount = serializers.SerializerMethodField(method_name='get_payment_amount')
    class Meta:
        model = IndividualPurchase
        fields = ['id', 'shipment_status', 'creation_date', 'payment_amount']

    def get_shipment_status(self,  obj):
        return obj.shipment.get_status_display()

    def get_payment_amount(self, obj):
        return obj.payment.amount_to_pay
    

class PaymentPUTSerializer(serializers.Serializer):
    payment_method_id = serializers.CharField()
    token = serializers.CharField()
    installments = serializers.IntegerField(min_value=1, max_value=24)
    payer_email = serializers.EmailField()
    payment_vendor = serializers.ChoiceField(choices=PAYMENT_VENDOR_CHOICES)


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'