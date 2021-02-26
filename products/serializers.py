# From drf
from rest_framework import routers, serializers, viewsets


# From w
from products.models import Product, Category


class ProductSerializer(serializers.ModelSerializer):
    measure_unit = serializers.CharField(source='get_measure_unit_display')
    class Meta:
        model = Product
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'description']

