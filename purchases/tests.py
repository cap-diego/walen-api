# From django
from django.test import TestCase
from django.test import Client
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.urls import reverse

# utils 
import json

# From ddf 
from ddf import G

# From w 
from purchases.models import Purchase, IndividualPurchase
from carts.models import Cart
from users.models import Address
from products.models import Product
from purchases.constants import PURCHASE_STATUS_PEND_INIT_PAY, \
    PAYMENT_STATUS_PENDING

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
        with self.assertRaises(ValidationError):
            purchase.clients_target = -1
            purchase.save()

    def test_clients_confirmed_cant_be_less_than_zero(self):
        purchase = G(Purchase)
        with self.assertRaises(IntegrityError):
            purchase.current_confirmed_clients = -1
            purchase.save()

    def test_clients_target_cant_be_zero(self):
        purchase = G(Purchase)
        with self.assertRaises(ValidationError):
            purchase.clients_target = 0
            purchase.save()

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


class PurchaseCartAPIIntegrationTest(TestCase):

    def test_create_purchase_blocks_associated_cart(self):
        c = Client()
        product = G(Product, unitary_price=50)
        cart = G(Cart)
        cart.add(prod_id=product.id, qt=1)
        purchase = G(Purchase, cart=cart)
        body = {
            "cart_id": '{}'.format(cart.id),
            "clients_target": 1,
            "shipment_area_center": {
                "city": "Buenos Aires",
                "state": "CABA",
                "floor_apt": "1",
                "address_line": "Maria ocampo 681",
                "country": "Argentina",
                "geocoding": None
            }
        }
        url = reverse('purchase-list')

        response = c.post(url, json.dumps(body), content_type='application/json')
        cart.refresh_from_db()
        assert response.status_code == 201
        assert cart.is_locked
    
    def test_cant_create_purchase_with_empty_cart(self):
        c = Client()
        cart = G(Cart)
        purchase = G(Purchase, cart=cart)
        body = {
            "cart_id": '{}'.format(cart.id),
            "clients_target": 1,
            "shipment_area_center": {
                "city": "Buenos Aires",
                "state": "CABA",
                "floor_apt": "1",
                "address_line": "Maria ocampo 681",
                "country": "Argentina",
                "geocoding": None
            }
        }
        url = reverse('purchase-list')

        response = c.post(url, json.dumps(body), content_type='application/json')
        cart.refresh_from_db()
        assert response.status_code == 400
        assert response.json() == 'error locking cart'


class IndividualPurchaseTest(TestCase):

    def test_payment_status_starts_on_pending(self):
        
        ind_purchase = G(IndividualPurchase)
        assert ind_purchase.payment.status == \
                    PAYMENT_STATUS_PENDING

    def test_shipment_status_starts_on_pending(self):
        
        ind_purchase = G(IndividualPurchase)
        assert ind_purchase.shipment.status == \
                    PAYMENT_STATUS_PENDING


    def test_body_creacion_individual_requiere_mail(self):
        c = Client()
        addr = G(Address)
        cart = G(Cart)
        purchase = G(Purchase, cart=cart)
        body = {
            'shipment_address': {
                'city': 'Buenos Aires',
                'state': 'CABA',
                'floor_apt': 'PB',
                'address_line': 'Avellaneda 281',
                'country': 'Argentina',
                'geocoding': None
            }
        }   

        url = reverse('purchase-individual',
                args=[purchase.id])
        response = c.post(url, json.dumps(body), content_type='application/json')
        assert response.status_code == 400


    def test_si_la_purchase_alcanzo_target_falla(self):
        c = Client()
        addr = G(Address)
        cart = G(Cart)
        purchase = G(Purchase, cart=cart, clients_target=1)
        body = {
            'client_email': 'fabio@gmail.com',
            'shipment_address': {
                'city': 'Buenos Aires',
                'state': 'CABA',
                'floor_apt': 'PB',
                'address_line': 'Avellaneda 281',
                'country': 'Argentina',
                'geocoding': None
            }
        }   

        url = reverse('purchase-individual',
                args=[purchase.id])
        response = c.post(url, json.dumps(body), content_type='application/json')
        assert response.status_code == 201

        body['client_email'] = 'fabricio@gmail.com'
        
        response = c.post(url, json.dumps(body), content_type='application/json')
        assert response.status_code == 400
        assert 'error, purchase already reached clients target' in response.json()


    def test_client_cant_have_multiple_individuals_to_same_purchase(self):
        c = Client()
        addr = G(Address)
        cart = G(Cart)
        purchase = G(Purchase, cart=cart, clients_target=2)
        body = {
            'client_email': 'fabio@gmail.com',
            'shipment_address': {
                'city': 'Buenos Aires',
                'state': 'CABA',
                'floor_apt': 'PB',
                'address_line': 'Avellaneda 281',
                'country': 'Argentina',
                'geocoding': None
            }
        }   

        url = reverse('purchase-individual',
                args=[purchase.id])
        response = c.post(url, json.dumps(body), content_type='application/json')
        assert response.status_code == 201

        response = c.post(url, json.dumps(body), content_type='application/json')
        assert response.status_code == 400
        assert 'error, client cant buy twice in the same purchase' in response.json()
