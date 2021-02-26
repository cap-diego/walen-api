# From django
from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError

# From DDF
from ddf import G

# From w 
from products.models import Product, Category

class ProductTestCase(TestCase):
    # fixtures = ['dumpdb.json']

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
