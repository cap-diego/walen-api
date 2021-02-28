# From django
from django.shortcuts import get_object_or_404
from django.db import transaction

# From drf 
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response 
from rest_framework import status
from rest_framework.exceptions import ValidationError

# From w 
from carts.models import Cart 
from carts.serializers import CartSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.prefetch_related('products')
    serializer_class = CartSerializer
    permission_classes = []

    @action(detail=True, methods=['POST'])
    @transaction.atomic
    def products(self, request, pk=None):
        cart = get_object_or_404(self.get_queryset(), pk=pk)
        if not isinstance(request.data, list):
            data = [request.data]
        else:
            data = request.data
        for prod_count in data:
            prod_id = int(prod_count.get('product', -1))
            count = int(prod_count.get('count', -1))
            if not cartprod_is_valid(prod_id, count):
                raise ValidationError('error, revise los campos')
            
            updated = cart.add(prod_id=prod_id, \
                                qt=count)
            if not updated:
                raise ValidationError('error updating cart')

        cart.refresh_from_db()
        cart_data = CartSerializer(cart).data
        return Response(cart_data)

def cartprod_is_valid(prod_id, count):
    if prod_id < 0 or count < 0:
        return False
    return True