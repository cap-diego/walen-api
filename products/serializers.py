# From drf
from rest_framework import serializers


# From w
from products.models import Product, Category, ProductReview, ProductPhoto

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'description']

class TagListingField(serializers.RelatedField):
    def to_representation(self, value):
        return value.tag

class ProductReviewPOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['product', 'author_name', 'commentary', 'rating', 'date']

class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['author_name', 'commentary', 'rating', 'date']


class ProductPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhoto
        fields = ['photo']

class ProductSerializer(serializers.ModelSerializer):
    measure_unit = serializers.CharField(source='get_measure_unit_display')
    tags = TagListingField(many=True, read_only=True)
    photos_url = serializers.SerializerMethodField(method_name="get_photosURL")
    last_review = serializers.SerializerMethodField(method_name="get_last_review")
    category = CategorySerializer()
    class Meta:
        model = Product
        fields = '__all__'

    def get_last_review(self, obj):
        if not obj.reviews.last():
            return None
        return ProductReviewSerializer(obj.reviews.last()).data


    def get_photosURL(self, obj):
        photos = ProductPhoto.objects.filter(product=obj)

        serializer = ProductPhotosSerializer(photos, many=True)
        
        return serializer.data

class ProductRecommendedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'featured_photo_url', 'display_name', 'description', 'unitary_price', 'measure_unit']

