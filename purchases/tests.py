# From djangoo
from django.test import TestCase
from django.test import Client
from django.db import IntegrityError
from django.core.exceptions import ValidationError

# From ddf 
from ddf import G

# From w 
from purchases.models import Purchase
from carts.models import Cart
from users.models import Address
from products.models import Product
from purchases.constants import PURCHASE_STATUS_PEND_INIT_PAY

class PurchaseTestCase(TestCase):

    def test_purchase_has_zero_discount_amount_by_default(self):
        purchase = G(Purchase)
        assert purchase.discount_amount == 0

    def test_purchase_has_zero_confirmed_clients_by_default(self):
        purchase = G(Purchase)
        assert purchase.current_confirmed_clients == 0

    def test_new_purchase_has_pending_initial_payment_status(self):
        purchase = G(Purchase)
        assert purchase.status == PURCHASE_STATUS_PEND_INIT_PAY

    def test_clients_target_cant_be_less_than_zero(self):
        purchase = G(Purchase)
        with self.assertRaises(IntegrityError):
            Purchase.objects.filter(pk=purchase.id).update(
                clients_target=-1
            )

    def test_clients_confirmed_cant_be_less_than_zero(self):
        purchase = G(Purchase)
        with self.assertRaises(IntegrityError):
            Purchase.objects.filter(pk=purchase.id).update(
                current_confirmed_clients=-1
            )        

    def test_clients_confirmed_cant_be_greater_than_target(self):
        purchase = G(Purchase, clients_target=1)
        purchase.add_confirmed_client()
        with self.assertRaises(ValidationError):
            purchase.add_confirmed_client()

    def test_amount_to_pay_is_cartprice_minus_amount_discount(self):
        product = G(Product, unitary_price=50)
        cart = G(Cart)
        cart.add(prod_id=product.id, qt=1)
        assert cart.total == 50
        purchase = G(Purchase, clients_target=1, 
                        discount_amount=10,
                        cart=cart)
        assert purchase.amount_to_pay == 40