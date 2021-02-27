# From django
from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.test import Client

# From DDF
from ddf import G

# From drf 
from django.urls import reverse

# From w 
from products.models import Product, Category, ProductReview

class ProductTestCase(TestCase):

    def test_category_desc_cant_be_repeated(self):
        categoria_limpieza = Category.objects.create(
            description='limpieza'
        )
        with self.assertRaises(IntegrityError):
            categoria_limpieza = Category.objects.create(
                description='limpieza'
        )

    def test_stock_product_cant_be_less_than_zero(self):
        with self.assertRaises(IntegrityError):
            p = Product.objects.create(
                display_name="Paty",
                unitary_price=100,
                current_stock=-10
            )
    
    def test_price_product_cant_be_less_than_0(self):
        with self.assertRaises(ValidationError):
            p = Product.objects.create(
                display_name="Paty",
                current_stock=10,
                unitary_price=-1
            )

    def test_product_list_includes_last_review(self):
        review = G(ProductReview, author_name='diego', commentary='todo ok')
        product_without_review = G(Product, description='Panchos')
        product_with_review = review.product
        c = Client()
        url = reverse('product-list')
        response = c.get(url)
        assert response.status_code == 200
        assert response.json()['results'][0]['last_review']['commentary'] \
            == 'todo ok'
        assert response.json()['results'][1]['last_review'] == None

    def test_product_includes_last_review(self):
        review = G(ProductReview, author_name='diego', commentary='todo ok')
        product = review.product
        c = Client()
        url = reverse('product-list')
        response = c.get('{}{}/reviews/'.format(url, product.id))
        assert response.status_code == 200
        assert response.json()['results'][0]['commentary'] == 'todo ok'
        url = reverse('product-detail', kwargs={'pk': product.id})
        response = c.get('{}'.format(url))
        assert response.status_code == 200
        assert response.json()['last_review']['commentary'] == 'todo ok'