# From drf
from rest_framework import routers, serializers, viewsets


# From w
from products.models import Product, Category

class TagListingField(serializers.RelatedField):
    def to_representation(self, value):
        return value.tag

class ProductSerializer(serializers.ModelSerializer):
    measure_unit = serializers.CharField(source='get_measure_unit_display')
    tags = TagListingField(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'description']

