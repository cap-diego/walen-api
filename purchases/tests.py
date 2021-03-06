# From django
from django.test import TestCase
from django.test import Client
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail

# utils 
import json
from unittest.mock import patch, MagicMock

# From ddf 
from ddf import G

# From w 
from purchases.models import Purchase, IndividualPurchase, \
    Payment, Coupon
from carts.models import Cart
from users.models import Address, Client as Cliente
from products.models import Product
from purchases.constants import PURCHASE_STATUS_PEND_INIT_PAY, \
    PAYMENT_STATUS_PENDING, SHIPMENT_STATUS_AWAITING_PAYMENT, \
    PAYMENT_VENDOR_MP, PURCHASE_STATUS_AWAITING_PEERS, \
    PURCHASE_STATUS_COMPLETED


User = get_user_model()

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

    def test_discount_is_zero_when_clients_target_is_one(self):
        product = G(Product, unitary_price=50)
        cart = G(Cart)
        cart.add(prod_id=product.id, qt=1)
        purchase = G(Purchase, clients_target=1, 
                        cart=cart)
        assert purchase.discount_amount == 0

    def test_amount_to_pay_is_cartprice_minus_amount_discount(self):
        product = G(Product, unitary_price=50)
        cart = G(Cart)
        cart.add(prod_id=product.id, qt=1)
        assert cart.total == 50
        purchase = G(Purchase, clients_target=2, 
                        cart=cart)
        expected_discount = (purchase.clients_target - 1) * 0.1 * cart.total
        assert purchase.amount == 50 - expected_discount 
        assert expected_discount == purchase.discount_amount
    
    def test_no_se_puede_cancelar_purchase_completed(self):
        purchase = G(Purchase)

        purchase.set_status_completed()

        with self.assertRaises(ValidationError):
            purchase.set_status_cancelled()


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

    def test_cant_create_purchase_if_stock_is_not_enough(self):
        c = Client()
        product = G(Product, unitary_price=50, current_stock=3)
        cart = G(Cart)
        cart.add(prod_id=product.id, qt=2)
        body = {
            "cart_id": '{}'.format(cart.id),
            "clients_target": 2,
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
        assert response.status_code == 400
        assert response.json() == 'error, cant create purchase because stock is not enough'

    def test_can_create_purchase_if_stock_is_enough(self):
        c = Client()
        product = G(Product, unitary_price=50, current_stock=4)
        cart = G(Cart)
        cart.add(prod_id=product.id, qt=2)
        body = {
            "cart_id": '{}'.format(cart.id),
            "clients_target": 2,
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
        assert response.status_code == 201

    def test_cant_cancel_purchase_completed(self):
        c = Client()
        purchase = G(Purchase)

        purchase.set_status_completed()

        url = reverse('purchase-cancel', args=[purchase.id])

        response = c.put(url)
        assert response.status_code == 400
        assert 'error, completed purchase cant be cancelled' in response.json()

class IndividualPurchaseTest(TestCase):

    def test_payment_status_starts_on_pending(self):
        
        ind_purchase = G(IndividualPurchase)
        assert ind_purchase.payment.status == \
                    PAYMENT_STATUS_PENDING

    def test_shipment_status_starts_on_awaiting_payment(self):
        
        ind_purchase = G(IndividualPurchase)
        assert ind_purchase.shipment.status == \
                    SHIPMENT_STATUS_AWAITING_PAYMENT

class IndividualPurchaseAPITest(TestCase):
    def body_ok(self):
        return {
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

    def body_no_ok(self): 
        return {
            'shipment_address': {
                'city': 'Buenos Aires',
                'state': 'CABA',
                'floor_apt': 'PB',
                'address_line': 'Avellaneda 281',
                'country': 'Argentina',
                'geocoding': None
            }
        }     
    def test_body_creacion_individual_requiere_mail(self):
        c = Client()
        addr = G(Address)
        cart = G(Cart)
        purchase = G(Purchase, cart=cart)
        url = reverse('individual-purchase-list',
                args=[purchase.id])
        response = c.post(url, json.dumps(self.body_no_ok()), content_type='application/json')
        assert response.status_code == 400

    def test_individual_purchase_not_change_purchase_clients_left(self):
        c = Client()
        addr = G(Address)
        cart = G(Cart)
        purchase = G(Purchase, cart=cart, clients_target=2)

        url = reverse('individual-purchase-list',
                args=[purchase.id])
        response = c.post(url, json.dumps(self.body_ok()), content_type='application/json')
        assert response.status_code == 201
        purchase.refresh_from_db()
        assert purchase.clients_left == 2

    def test_client_cant_have_multiple_individuals_with_reserved_payment_to_same_purchase(self):
        c = Client()
        addr = G(Address)
        cart = G(Cart)
        purchase = G(Purchase, cart=cart, clients_target=2)
        url = reverse('individual-purchase-list',
                args=[purchase.id])
        response = c.post(url, json.dumps(self.body_ok()), content_type='application/json')
        assert response.status_code == 201
        
        purchase.individuals_purchases.all()[0].payment.set_status_reserved()

        response = c.post(url, json.dumps(self.body_ok()), content_type='application/json')
        assert response.status_code == 400
        assert 'error, client cant buy twice in the same purchase' in response.json()

    def test_list_individual_purchase(self):
        c = Client()
        ind = G(IndividualPurchase)
        url = reverse('individual-purchase-detail', \
            args=[ind.pk])
        response = c.get(url)

        assert response.status_code == 200

    def test_si_la_purchase_alcanzo_target_falla_la_creac_de_individual(self):
        c = Client()
        addr = G(Address)
        cart = G(Cart)
        purchase = G(Purchase, cart=cart, clients_target=1)
        purchase.add_confirmed_client()
        url = reverse('individual-purchase-list',
                args=[purchase.id])        
        response = c.post(url, json.dumps(self.body_ok()), content_type='application/json')
        assert response.status_code == 400
        assert 'error, purchase already reached clients target' in response.json()

    @patch('ecommerceapp.time.APIClock')
    def test_add_individual_to_expired_purchase_fails(self, mock):
        c = Client()
        addr = G(Address)
        cart = G(Cart)
        purchase = G(Purchase, cart=cart, clients_target=1)
        
        mock.date_is_expired().return_value = True

        url = reverse('individual-purchase-list',
                args=[purchase.id])  
        
        response = c.post(url, json.dumps(self.body_ok()), content_type='application/json')

        assert response.status_code == 400
        assert response.json() == 'error, purchase expired'

    def test_cant_create_individual_to_cancelled_purchase(self):
        c = Client()
        addr = G(Address)
        cart = G(Cart)
        purchase = G(Purchase, cart=cart, clients_target=2)
        purchase.set_status_cancelled()
        url = reverse('individual-purchase-list',
                args=[purchase.id])
        response = c.post(url, json.dumps(self.body_ok()), content_type='application/json')
        assert response.status_code == 404

class PaymentVendorIntegrationTestCase(TestCase):
    
    @patch('purchases.payment_vendors.mercadopago.MercadoPagoPaymentService')
    def test_al_reservar_pago_payment_se_actualiza_payment_status(self, mock):
        c = Client()
        res = {'id': 13654}
        mock.do.return_value = (res, True) 
        purchase = G(Purchase, clients_target=2)
        ind_purchase = G(IndividualPurchase)
        payment = ind_purchase.payment
   
        url = reverse('payment-vendor-detail', args=[payment.id])

        response = c.put(url, json.dumps(self.body_ok()), content_type='application/json')
        payment.refresh_from_db()
        assert response.status_code == 200
        assert payment.is_reserved
        assert payment.vendor_payment_id == res['id']
        assert payment.vendor_name == PAYMENT_VENDOR_MP

    def body_ok(self):
        return  {
            "token": "224cbedda052cdda1fb36f1eb51d4d2b",
            "payment_method_id": "visa",
            "installments": 1,
            "payer_email": "fabio12345@gmail.com",
            "payment_vendor": PAYMENT_VENDOR_MP
        }   

    def test_no_se_puede_reservar_dos_veces_el_mismo_pago(self):
        c = Client()
        purchase = G(Purchase, clients_target=2)
        ind_purchase = G(IndividualPurchase)
        payment = ind_purchase.payment
        payment.set_status_reserved()

        url = reverse('payment-vendor-detail', args=[payment.id])

        response = c.put(url, json.dumps(self.body_ok()), 
            content_type='application/json')        
        assert response.status_code == 400
    
    @patch('purchases.payment_vendors.mercadopago.MercadoPagoPaymentService')
    def test_si_falla_reserva_payment_status_queda_en_failed(self, mock):
        c = Client()
        mock.do.return_value = (None, False) 
        purchase = G(Purchase, clients_target=2)
        ind_purchase = G(IndividualPurchase)
        payment = ind_purchase.payment
   
        url = reverse('payment-vendor-detail', args=[payment.id])

        response = c.put(url, json.dumps(self.body_ok()), 
            content_type='application/json')
        payment.refresh_from_db()
        assert response.status_code == 400
        assert payment.failed

    @patch('purchases.payment_vendors.mercadopago.MercadoPagoPaymentService')
    def test_es_posible_reintentar_pago_fallado(self, mock):
        c = Client()
        mock.do.return_value = ({'id': 23232}, True) 
        purchase = G(Purchase, clients_target=2)
        ind_purchase = G(IndividualPurchase)
        payment = ind_purchase.payment
        payment.set_status_failed()
        url = reverse('payment-vendor-detail', args=[payment.id])

        response = c.put(url, json.dumps(self.body_ok()), 
            content_type='application/json')
        payment.refresh_from_db()
        assert response.status_code == 200
        assert payment.is_reserved

    @patch('purchases.payment_vendors.mercadopago.MercadoPagoPaymentService')    
    def test_si_el_payment_se_reserva_se_descuenta_clients_left_de_purchase(self, mock):
        c = Client()
        res = {'id': 13654}
        mock.do.return_value = (res, True) 
        purchase = G(Purchase, clients_target=2)
        ind_purchase = G(IndividualPurchase, purchase=purchase)
        payment = ind_purchase.payment
        before = purchase.clients_left

        url = reverse('payment-vendor-detail', args=[payment.id])

        response = c.put(url, json.dumps(self.body_ok()), content_type='application/json')
        purchase.refresh_from_db()
        assert response.status_code == 200 
        assert purchase.clients_left == before - 1
    

    @patch('purchases.payment_vendors.mercadopago.MercadoPagoPaymentService')    
    def test_si_el_payment_falla_no_se_descuenta_clients_left_de_purchase(self, mock):
        c = Client()
        mock.do.return_value = (None, False) 
        purchase = G(Purchase, clients_target=5)
        ind_purchase = G(IndividualPurchase, purchase=purchase)
        payment = ind_purchase.payment
        before = purchase.clients_left

        url = reverse('payment-vendor-detail', args=[payment.id])

        response = c.put(url, json.dumps(self.body_ok()), content_type='application/json')
        purchase.refresh_from_db()
        assert response.status_code == 400
        assert purchase.clients_left == before
    

    @patch('purchases.payment_vendors.mercadopago.MercadoPagoPaymentService')    
    @patch('ecommerceapp.time.APIClock')
    def test_es_posible_actualizar_payment_con_Purchase_expirada(self, mock_time, mock_mp):
        c = Client()
        addr = G(Address)
        cart = G(Cart)
        purchase = G(Purchase, cart=cart, clients_target=3)
        ind_purchase = G(IndividualPurchase, purchase=purchase)
        mock_mp.do.return_value = ({'id': 13654}, True) 
        mock_time.date_is_expired().return_value = True
        before = purchase.clients_left
        payment = ind_purchase.payment

        url = reverse('payment-vendor-detail', args=[payment.id])
        response = c.put(url, json.dumps(self.body_ok()), content_type='application/json')
        purchase.refresh_from_db()
        assert response.status_code == 200 
        assert purchase.clients_left == before - 1

class PurchasePaymentsAPIIntegrationTestCase(TestCase):

    def body_ok(self):
        return  {
            "token": "224cbedda052cdda1fb36f1eb51d4d2b",
            "payment_method_id": "visa",
            "installments": 1,
            "payer_email": "fabio12345@gmail.com",
            "payment_vendor": PAYMENT_VENDOR_MP
        }   
    
    @patch('purchases.payment_vendors.mercadopago.MercadoPagoPaymentService')    
    def test_primer_payment_pone_purchase_en_awaiting_peers(self, mock):
        c = Client()
        res = {'id': 13654}
        mock.do.return_value = (res, True) 
        purchase = G(Purchase, clients_target=2)
        ind_purchase = G(IndividualPurchase, purchase=purchase)
        payment = ind_purchase.payment
        before = purchase.clients_left

        url = reverse('payment-vendor-detail', args=[payment.id])

        response = c.put(url, json.dumps(self.body_ok()), content_type='application/json')
        purchase.refresh_from_db()
        assert response.status_code == 200 
        assert purchase.status == PURCHASE_STATUS_AWAITING_PEERS

    @patch('purchases.payment_vendors.mercadopago.MercadoPagoPaymentService')
    def test_cuando_purchase_alcanza_clients_target_status_es_completed(self, mock):
        c = Client()
        res = {'id': 13654}
        mock.do.return_value = (res, True) 
        mock.capture.return_value = (None, True)
        purchase = G(Purchase, clients_target=1)
        ind_purchase = G(IndividualPurchase, purchase=purchase)
        payment = ind_purchase.payment
        before = purchase.clients_left

        url = reverse('payment-vendor-detail', args=[payment.id])

        response = c.put(url, json.dumps(self.body_ok()), content_type='application/json')
        purchase.refresh_from_db()
        assert response.status_code == 200 
        assert purchase.status == PURCHASE_STATUS_COMPLETED

    @patch('purchases.payment_vendors.mercadopago.MercadoPagoPaymentService')
    def test_completed_purchase_triggers_payment_capturing(self, mock):
        c = Client()
        mock.capture.return_value = (None, True)
        purchase = G(Purchase, clients_target=1)
        ind_purchase = G(IndividualPurchase, purchase=purchase)
        payment = ind_purchase.payment
        purchase.set_status_completed()

        payment.refresh_from_db()
        assert payment.is_captured

    def test_cancel_purchase(self):
        c = Client()
        purchase = G(Purchase, clients_target=2)

        url = reverse('purchase-cancel', args=[purchase.id])

        response = c.put(url)
        assert response.status_code == 204


class PurchaseSignalTestCase(TestCase):

    @patch('purchases.signals.update_purchase_related_models_status')
    def test_purchase_clients_target_reached_se_pone_completed(self, mock):
        
        purchase = G(Purchase,  clients_target=1)
        purchase.add_confirmed_client()
        purchase.refresh_from_db()
        assert purchase.is_completed
    
    def test_payment_reserved_status_triggers_shipment_awaiting_purch_comp(self):
        purchase = G(Purchase, clients_target=1)
        individual = G(IndividualPurchase, purchase=purchase)
        payment = individual.payment
        payment.set_status_reserved()
        
        shipment = individual.shipment

        assert shipment.is_awaiting_purchase_completition   


    def test_payment_captured_status_triggers_shipment_pending(self):
        purchase = G(Purchase, clients_target=1)
        individual = G(IndividualPurchase, purchase=purchase)
        payment = individual.payment

        payment.set_status_captured()
        
        shipment = individual.shipment
        
        shipment.refresh_from_db()

        assert shipment.is_pending   
    
    def test_purchase_cancelled_puts_payment_cancelled(self):
        individual = G(IndividualPurchase)
        payment = individual.payment

        payment.set_status_cancelled()

        shipment = individual.shipment
        
        shipment.refresh_from_db()

        assert payment.is_cancelled

    def test_payment_cancelled_puts_shipment_aborted(self):
        individual = G(IndividualPurchase)
        payment = individual.payment

        payment.set_status_cancelled()

        shipment = individual.shipment
        
        shipment.refresh_from_db()

        assert shipment.is_aborted
    

class PurchaseNotificationEmailTestCase(TestCase):
    
    def test_purchase_completed_and_payments_captured_notifies_users(self):
        purchase = G(Purchase, clients_target=2)
        
        client_1 = G(Cliente, email="pedro@gmail.com")
        client_2 = G(Cliente, email="mariana@gmail.com")

        individual1 = G(IndividualPurchase, 
            purchase=purchase, client=client_1)

        individual2 = G(IndividualPurchase, 
            purchase=purchase, client=client_2)
        
        individual1.payment.set_status_captured()
        individual2.payment.set_status_captured()
        purchase.set_status_completed()

        self.assertEqual(len(mail.outbox), purchase.clients_target)

        self.assertEqual(mail.outbox[0].subject, 'Pago realizado')


    def test_purchase_completed_and_not_all_payments_captured_no_notifies_users(self):
        purchase = G(Purchase, clients_target=2)
        
        client_1 = G(Cliente, email="pedro@gmail.com")
        client_2 = G(Cliente, email="mariana@gmail.com")

        individual1 = G(IndividualPurchase, 
            purchase=purchase, client=client_1)

        individual2 = G(IndividualPurchase, 
            purchase=purchase, client=client_2)
        
        individual1.payment.set_status_captured()
        
        purchase.set_status_completed()

        self.assertEqual(len(mail.outbox), 0)


    def test_shipment_dispatched_notify_user(self):
        purchase = G(Purchase, clients_target=1)
        
        client = G(Cliente, email="pedro@gmail.com")

        individual = G(IndividualPurchase, 
            purchase=purchase, client=client)  

        individual.shipment.set_status_dispatched()

        subject = 'Estado compra'

        subject_enviados = ''
        for i in range(len(mail.outbox)):
            subject_enviados = mail.outbox[i].subject + " "

        assert subject in subject_enviados


    def test_shipment_delivered_notify_user(self):
        purchase = G(Purchase, clients_target=1)
        
        client = G(Cliente, email="pedro@gmail.com")

        individual = G(IndividualPurchase, 
            purchase=purchase, client=client)  

        individual.shipment.set_status_delivered()

        subject = 'Estado compra'

        subject_enviados = ''
        for i in range(len(mail.outbox)):
            subject_enviados = mail.outbox[i].subject + " "

        assert subject in subject_enviados


class PaymentCouponTestcase(TestCase):
    
    def test_payment_with_coupon_has_discount(self):
        
        product = G(Product, unitary_price=50)
        cart = G(Cart)
        cart.add(prod_id=product.id, qt=1)
        purchase = G(Purchase, clients_target = 1, \
            cart=cart) 

        ind_purchase = G(IndividualPurchase, 
            purchase=purchase)

        payment = ind_purchase.payment
        
        assert payment.amount_to_pay == purchase.amount
        
        coupon = G(Coupon, discount_percent=10)

        payment.add_coupon(coupon)

        assert payment.amount_to_pay == 45


class PaymentCouponAPITestCase(TestCase):

    def test_can_add_to_payment(self):
        c = Client()
        payment = G(Payment)

        url = reverse('payment-coupon', args=[payment.id])
        coupon = G(Coupon)
        body = {'coupon_id': '{}'.format(coupon.id)}
        response = c.put(url, json.dumps(body), content_type='application/json')

        assert response.status_code == 200

        payment.refresh_from_db()
        assert payment.has_coupon


class CouponAPITestCase(TestCase):

    def test_coupon_vencido_no_se_lista(self):
        c = Client()
        
        from ecommerceapp.time import APIClock
        from datetime import timedelta
        tomorrow = APIClock.now() + timedelta(days=1)
        yesterday = APIClock.now() - timedelta(days=1)
        coupon_no_vencido = G(Coupon, valid_until=tomorrow)
        coupon_vencido = G(Coupon, valid_until=yesterday)

        url = reverse('coupon-list')

        response = c.get(url)

        assert response.status_code == 200

        assert len(response.json()) == 1
        assert response.json()[0]['id'] == str(coupon_no_vencido.id)
