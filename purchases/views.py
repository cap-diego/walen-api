# From django 
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError

# From drf 
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError

# From w
from purchases.models import Purchase, IndividualPurchase, \
    get_create_individual_purchase, \
    Payment, Shipment, Coupon, purchase_history, \
    purchase_recommendations    

from ecommerceapp import time
from purchases.serializers import PurchaseGETSerializer, \
    PurchasePOSTSerializer, IndividualPurchasePOSTSerializer, \
    IndividualPurchaseGETSerializer, PaymentSerializer, \
    ShipmentSerializer, PaymentPUTSerializer, CouponSerializer, \
    IndividualPurchaseMiniGETSerializer    

from users.auth.utils import did_token_required, \
    email_in_url_required

from users.models import Client, get_or_create_client, \
    create_address
from users.serializers import AddressSerializer

from purchases.constants import PAYMENT_VENDOR_MP, \
    PURCHASE_STATUS_CANCELLED
from purchases.payment_vendors import mercadopago
from carts.models import CartProduct
from products.serializers import ProductRecommendedSerializer

PurchasesNoCancelled = \
    Purchase.objects.exclude(status=PURCHASE_STATUS_CANCELLED)


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
    stock_enough = stock_is_enough_for_cart(
                    clients_target=clients_target,
                    cart_id=cart_id)

    if not stock_enough:
        return Response('error, cant create purchase because stock is not enough',
            status=status.HTTP_400_BAD_REQUEST)

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

def stock_is_enough_for_cart(clients_target, cart_id):
    cartprods = CartProduct.objects.filter(cart_id=cart_id)
    for cp in cartprods:
        if not stock_is_enough(cp.product, cp.count, clients_target):
            return False
    return True

def stock_is_enough(prod, qt, cant_clients):
    if prod.current_stock < (qt * cant_clients):
        return False
    return True

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

    purchase = get_object_or_404(PurchasesNoCancelled, pk=purchase_id)
    serializer = IndividualPurchasePOSTSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response('{}'.format(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
    serializer_data = serializer.data
    
    if time.APIClock.date_is_expired(purchase.expiration_date):
        error_msg = 'error, purchase expired'
        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

    if purchase.clients_target_reached:
        error_msg = 'error, purchase already reached clients target'
        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

    client = get_or_create_client(serializer.data['client_email'])
    addr, err = create_address(serializer_data['shipment_address'])
    
    if err:
        return Response('error al crear address: {}'.format(err), status=status.HTTP_400_BAD_REQUEST)        

    individual, err = get_create_individual_purchase(purchase, client, addr)
        
    if err:
        return Response('error al crear individual: {}'.format(err), status=status.HTTP_400_BAD_REQUEST)

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

    data['transaction_amount'] = payment.amount_to_pay

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


@api_view(['PUT'])
@permission_classes([])
def cancel_puchase_view(request, purchase_id):
    
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    try:
        purchase.set_status_cancelled()
    except DjangoValidationError as err:
        return Response('{}'.format(err), status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['PUT'])
@permission_classes([])
def payment_add_coupon_view(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    coupon_id = request.data.get('coupon_id', None)
    
    if not coupon_id:
        return Response('error, coupon id', status=status.HTTP_400_BAD_REQUEST)
    
    coupon = get_object_or_404(Coupon, pk=coupon_id)

    payment.add_coupon(coupon)

    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([])
def coupons_list_view(request):
    
    now = time.APIClock.now()

    coupons = Coupon.objects.filter(valid_until__gte=now)
    serializer = CouponSerializer(coupons, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([])
@did_token_required
@email_in_url_required
def purchase_history_view(request, email):
    """
        Get the last 10 purchases
    """
    client = get_object_or_404(Client, email=email)

    individuals = purchase_history(client, 10)

    serializer = IndividualPurchaseMiniGETSerializer(individuals, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([])
@did_token_required
@email_in_url_required
def purchase_recommendations_view(request, email):

    client = get_object_or_404(Client, email=email)

    res = purchase_recommendations(client)
    serializer = ProductRecommendedSerializer(res, many=True)
    return Response(serializer.data)




def get_or_create_addr(addr):
    if addr is None:
        return None, ''

    serializer = AddressSerializer(data=addr)
    if not serializer.is_valid():
        return None, '{}'.format(serializer.errors)
    try:
        addr = serializer.save()
    except Exception as err:
        return None, 'error creating Address:  [{}]'.format(err)

    return addr, ''