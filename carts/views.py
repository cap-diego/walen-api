# From django
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

# From drf 
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response 
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser

# From w 
from carts.models import Cart 
from carts.serializers import CartSerializer
from products.models import Product

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.prefetch_related('products')
    serializer_class = CartSerializer
    permission_classes = []

    def update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_permissions(self):
        permission_classes = []
        if self.action == 'list':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

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
            res, err = body_is_valid(prod_id, count)
            if err:
                raise ValidationError('error: {}'.format(err))
            updated = cart.add(prod_id=prod_id, \
                                qt=count)
            if not updated:
                raise ValidationError('error updating cart')

        cart.refresh_from_db()
        cart_data = CartSerializer(cart).data
        return Response(cart_data)

def body_is_valid(prod_id, count):
    if prod_id < 0 or count < 0:
        return False, 'revise los campos'
    return prod_is_valid(prod_id)

def prod_is_valid(prod_id):
    try:
        Product.objects.get(id=prod_id)
    except ObjectDoesNotExist:
        return False, 'producto {} no existe'.format(prod_id)
    return True, ''
