# From django 
from django.shortcuts import get_object_or_404
from django.db import transaction

# From drf 
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError

# From w
from purchases.models import Purchase, IndividualPurchase, \
    create_shipment, create_payment, create_individual_purchase, \
        get_or_create_addr, Payment, Shipment

from purchases.serializers import PurchaseGETSerializer, \
    PurchasePOSTSerializer, IndividualPurchasePOSTSerializer, \
        IndividualPurchaseGETSerializer, PaymentSerializer, \
            ShipmentSerializer, PaymentPUTSerializer

from users.models import Client, get_or_create_client, \
    get_or_create_address

from purchases.constants import PAYMENT_VENDOR_MP
from purchases.payment_vendors import mercadopago


@api_view(['POST'])
@permission_classes([])
def create_purchase_view(request):
    addr = request.data.pop('shipment_area_center', None)
    info, err = serialize_purchase_info(request.data)
    if err:
        return Response('invalid body: {}'.format(err), status=status.HTTP_400_BAD_REQUEST)
    clients_target = info['clients_target']
    cart_id = info['cart_id']

    ship_area, err = get_or_create_addr(addr)

    if err:
        return Response('error with shipment area body: {}'.format(err),
            status=status.HTTP_400_BAD_REQUEST)
    
    try:
        purchase = Purchase.objects.create(
            clients_target=clients_target,
            cart_id=cart_id,
            shipment_area_center=ship_area
        )
    except Exception:
        return Response('error creating purchase',
            status=status.HTTP_400_BAD_REQUEST)

    locked = purchase.cart.lock()
    if not locked:
        return Response('error locking cart',
            status=status.HTTP_400_BAD_REQUEST)

    serializer = PurchaseGETSerializer(purchase)

    return Response(serializer.data, status=status.HTTP_201_CREATED)    


def serialize_purchase_info(data):
    serializer = PurchasePOSTSerializer(data=data)
    if not serializer.is_valid():
        return None, '{}'.format(serializer.errors)
        
    return serializer.data, ''

@api_view(['GET'])
@permission_classes([])
def get_purchase_view(request, purchase_id):
    obj = get_object_or_404(Purchase, pk=purchase_id)
    serializer = PurchaseGETSerializer(obj)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([])
@transaction.atomic
def create_individual_purchase_view(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    serializer = IndividualPurchasePOSTSerializer(data=request.data)
    if not serializer.is_valid():
        return Response('{}'.format(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
    serializer_data = serializer.data
    
    if purchase.clients_target_reached:
        error_msg = 'error, purchase already reached clients target'
        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

    client = get_or_create_client(serializer.data['client_email'])
    addr = get_or_create_address(serializer_data['shipment_address'])
    individual, err = create_individual_purchase(purchase, client, addr)
        
    if err:
        return Response('{}'.format(err), status=status.HTTP_400_BAD_REQUEST)

    serializer = IndividualPurchaseGETSerializer(individual)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([])
def list_individual_purchase_view(request, ind_purch_id):
    individual_purchase = get_object_or_404(IndividualPurchase, pk=ind_purch_id)

    serializer = IndividualPurchaseGETSerializer(individual_purchase)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([])
def detail_payment_view(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    serializer = PaymentSerializer(payment)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([])
def detail_shipment_view(request, shipment_id):
    payment = get_object_or_404(Shipment, pk=shipment_id)
    serializer = ShipmentSerializer(payment)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([])
@transaction.atomic
def create_payment_view(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    purchase = payment.individual_purchase.purchase
    serializer = PaymentPUTSerializer(data=request.data)
    if payment.is_reserved:
        error_msg = 'el pago ya esta reservado'
        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

    if not serializer.is_valid():
        return Response('error: {}'.format(serializer.errors),
            status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.data
    vendor_name = data['payment_vendor']

    data['transaction_amount'] = purchase.amount_to_pay
    data.pop('payment_vendor')

    if vendor_name == PAYMENT_VENDOR_MP:
        res, ok = mercadopago.MercadoPagoPaymentService.do(data=data)

    if not ok:
        payment.save_vendor_info(None, vendor_name)
        payment.set_status_failed()
        return Response('{}'.format(res), status=status.HTTP_400_BAD_REQUEST)

    payment.save_vendor_info(res.get('id', None), vendor_name)
    payment.set_status_reserved()
    purchase.set_status_awaiting_peers()
    try:
        purchase.add_confirmed_client()
    except Exception as err:
        raise ValidationError(err.message)

    return Response(status=status.HTTP_200_OK)