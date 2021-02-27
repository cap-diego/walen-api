# From drf
from rest_framework import serializers


# From w
from products.models import Product, Category, ProductReview

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'description']

class TagListingField(serializers.RelatedField):
    def to_representation(self, value):
        return value.tag

class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['author_name', 'commentary', 'rating', 'date']

class ProductSerializer(serializers.ModelSerializer):
    measure_unit = serializers.CharField(source='get_measure_unit_display')
    tags = TagListingField(many=True, read_only=True)
    last_review = serializers.SerializerMethodField(method_name="get_last_review")
    category = CategorySerializer()
    class Meta:
        model = Product
        fields = '__all__'

    def get_last_review(self, obj):
        if not obj.reviews.last():
            return None
        return ProductReviewSerializer(obj.reviews.last()).data



