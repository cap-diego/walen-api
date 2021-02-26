# From django
from django.http import HttpResponse

# From drf 
from rest_framework import routers, serializers, viewsets
from rest_framework.pagination import PageNumberPagination

# From w 
from products.models import Product, Category 
from products.serializers import ProductSerializer, CategorySerializer


class NormalPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = NormalPagination