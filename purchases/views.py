# From django 
from django.shortcuts import get_object_or_404

# From drf 
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

# From 
from purchases.models import Purchase
from purchases.serializers import PurchaseGETSerializer, \
    PurchasePOSTSerializer
from users.serializers import AddressSerializer

@api_view(['POST'])
@permission_classes([])
def create_purchase(request):
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

    serializer = PurchaseGETSerializer(purchase)

    return Response(serializer.data, status=status.HTTP_201_CREATED)    


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
    
def serialize_purchase_info(data):
    serializer = PurchasePOSTSerializer(data=data)
    if not serializer.is_valid():
        return None, True
        
    return serializer.data, False

@api_view(['GET'])
@permission_classes([])
def get_purchase(request, purchase_id):
    obj = get_object_or_404(Purchase, pk=purchase_id)
    serializer = PurchaseGETSerializer(obj)
    return Response(serializer.data, status=status.HTTP_200_OK)
