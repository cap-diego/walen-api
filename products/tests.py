# From django
from django.test import TestCase

# From w 
from products.models import Product, Category

class ProductTestCase(TestCase):
    def setUp(self):
        # Product.objects.create(
        #     display_name="Glade"
        #     description="Aerosol de cocina"
        #     featured_photo_url="https://asd.com"
        #     photo_url="https://asd.com"
        #     unitary_price=20,

        # )

        categoria_limpieaza = Category.objects.create(
            description='limpieza'
        )

    def test_categoria_limpieza(self):
        self.assertEqual(self.categoria_limpieaza, 'The lion says "roar"')