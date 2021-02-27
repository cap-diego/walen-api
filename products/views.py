# From django
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

# From drf 
from rest_framework import routers, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# From w 
from products.models import Product, Category 
from products.serializers import ProductSerializer, \
    CategorySerializer, ProductReviewSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects \
            .select_related('category') \
            .prefetch_related('reviews') \
            .prefetch_related('tags') 

    serializer_class = ProductSerializer

    @action(detail=True, methods=['GET'])
    def reviews(self, request, pk=None):
        product = get_object_or_404(self.queryset, pk=pk)
        reviews = product.reviews.values()
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ProductReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer