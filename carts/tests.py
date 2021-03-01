# From django
from django.test import TestCase
from django.test import Client

# From drf 
from rest_framework.reverse import reverse

# From DDF
from ddf import G, N

# From w
from carts.models import Cart
from products.models import Product


class CartModelTest(TestCase):
    
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
        res = cart.add(prod_id=prod.id, qt=1)
        assert res == 1
        assert not cart.is_empty
        assert cart.total == prod.unitary_price

    def test_item_with_qt_0_is_removed(self):
        cart = G(Cart)
        prod = G(Product, unitary_price=100.0)
        cart.add(prod_id=prod.id, qt=1)
        res = cart.add(prod_id=prod.id, qt=0)
        assert res == 1
        assert cart.is_empty

    def test_item_with_new_qt_is_updated(self):
        cart = G(Cart)
        prod = G(Product, unitary_price=10.0)
        cart.add(prod_id=prod.id, qt=1)
        res = cart.add(prod_id=prod.id, qt=2)
        assert res == 1
        assert not cart.is_empty


    def test_locked_cart_cant_add(self):
        cart = G(Cart)
        prod = G(Product, unitary_price=10.0)
        cart.add(prod_id=prod.id, qt=1)
        cart.lock()
        assert cart.is_locked
        res = cart.add(prod_id=prod.id, qt=2)
        assert res == 0


class CartAPITest(TestCase):
    

    def test_create_new_cart_empty_and_nonlocked(self):
        c = Client()
        url = reverse('cart-list')
        response = c.post(url)
        assert response.status_code == 201
        assert response.json()['total'] == 0
        assert response.json()['id']
        assert response.json()['is_empty']
        assert not response.json()['is_locked']
        assert len(response.json()['products']) == 0


    def test_get_cart(self):
        c = Client()
        cart = G(Cart)
        url = reverse('cart-detail', kwargs={'pk': cart.id})
        response = c.get(url)
        assert response.status_code == 200

    def test_add_product_to_cart(self):
        c = Client()
        cart = G(Cart)
        prod = G(Product)
        body = {
                "product": prod.id,
                "count": 1,
                }
        url = reverse('cart-detail', kwargs={"pk": cart.id})
        response = c.post('{}products/'.format(url), body)
        assert response.status_code == 200
        assert not response.json()['is_empty']
        assert response.json()['products']


    def test_atomic_when_error_updating_cart(self):
        c = Client()
        cart = G(Cart)
        prod = G(Product)
        body = {
                "product": prod.id,
                "count": 1,
                }
        url = reverse('cart-detail', kwargs={"pk": cart.id})
        response = c.post('{}products/'.format(url), body)
        total_before = response.json()['total']
        body['count'] = -2
        response = c.post('{}products/'.format(url), body)
        assert response.status_code == 400
        assert cart.products.count() == 1
        response = c.get(url)
        assert total_before == response.json()['total']

    def test_error_when_body_is_not_correct(self):
        c = Client()
        cart = G(Cart)
        prod = G(Product)
        body = {
                "no_product_key": prod.id,
                "no_count_key": 1,
                }
        url = reverse('cart-detail', kwargs={"pk": cart.id})
        response = c.post('{}products/'.format(url), body)
        assert response.status_code == 400

    def test_add_product_no_exists_error(self):
        c = Client()
        cart = G(Cart)
        prod = G(Product)
        invalid_prod_id = 2323
        body = {
                "product": invalid_prod_id,
                "count": 1,
                }
        url = reverse('cart-detail', kwargs={"pk": cart.id})
        response = c.post('{}products/'.format(url), body)
        assert response.status_code == 400
