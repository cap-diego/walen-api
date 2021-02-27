# From django
from django.test import TestCase

# From w
from carts.models import Cart
from products.models import Product

# From DDF
from ddf import G, N

class CartTest(TestCase):
    
    def test_new_cart_is_empty(self):
        cart = N(Cart)
        assert cart.is_empty

    def test_new_cart_is_unlocked(self):
        cart = N(Cart)
        assert not cart.is_locked

    def test_new_cart_has_total_of_zero(self):
        cart = N(Cart)
        assert cart.total == 0

    def test_new_item_to_cart(self):
        cart = G(Cart)
        prod = G(Product, unitary_price=100.0)
        res = cart.add(prod=prod, qt=1)
        assert res == 1
        assert not cart.is_empty
        assert cart.total == prod.unitary_price

    def test_item_with_qt_0_is_removed(self):
        cart = G(Cart)
        prod = G(Product, unitary_price=100.0)
        cart.add(prod=prod, qt=1)
        res = cart.add(prod=prod, qt=0)
        assert res == 1
        assert cart.is_empty

    def test_item_with_new_qt_is_updated(self):
        cart = G(Cart)
        prod = G(Product, unitary_price=10.0)
        cart.add(prod=prod, qt=1)
        res = cart.add(prod=prod, qt=2)
        assert res == 1
        assert not cart.is_empty


    def test_locked_cart_cant_add(self):
        cart = G(Cart)
        prod = G(Product, unitary_price=10.0)
        cart.add(prod=prod, qt=1)
        cart.lock()
        assert cart.is_locked
        res = cart.add(prod=prod, qt=2)
        assert res == 0




