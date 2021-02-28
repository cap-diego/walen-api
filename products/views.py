# From django
from django.shortcuts import get_object_or_404

# From drf 
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

# From w 
from products.models import Product, Category 
from products.serializers import ProductSerializer, \
    CategorySerializer, ProductReviewSerializer, ProductReviewPOSTSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects \
            .select_related('category') \
            .prefetch_related('reviews') \
            .prefetch_related('tags') 

    serializer_class = ProductSerializer
    permission_classes = []

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
    
    @action(detail=True, methods=['POST'])
    def new_review(self, request, pk=None):
        serializer = ProductReviewPOSTSerializer(data=request.data)
        if not serializer.is_valid():
            return Response('body review invalido', status=status.HTTP_400_BAD_REQUEST)
        review = serializer.save()
        
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer