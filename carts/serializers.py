# From drf
from rest_framework import serializers

# From w
from carts.models import Cart, CartProduct

class CartProductGETSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartProduct
        fields = ['product', 'count']

class CartSerializer(serializers.ModelSerializer):
    
    products = serializers.SerializerMethodField(method_name='get_products')
    class Meta:
        model = Cart
        fields = [
            'id', 'created_at', \
            'is_locked', 'total', 'is_empty', 'products'
        ]

    def get_products(self, obj):
        cartprods = CartProduct.objects.filter(cart=obj)
        serializer = CartProductGETSerializer(cartprods, many=True)
        return serializer.data