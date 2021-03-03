from django.db import transaction
from django.core import mail
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

from purchases.payment_vendors import mercadopago
from purchases.constants import PAYMENT_STATUS_CAPTURED
from ecommerceapp.email import send_email_purchase

def update_purchase_related_models_status(sender, **kwargs):
    purchase = kwargs['instance']

    if purchase.is_cancelled:
        cancel_payments(purchase)
        return

    if purchase.is_completed:
        capture_payments_purchase(purchase)
        check_if_notify_clients(purchase)
        return

    if purchase.clients_target_reached:
        purchase.set_status_completed()
        return


def check_if_notify_clients(purchase):
    """
        Si todos los payments estan capturados entonces
        envia un mail a los clientes de las individual
        purchases asociadas a la Purchase grupal
    """
    individuals = purchase.individuals_purchases
    no_capturadas = individuals.exclude(payment__status=PAYMENT_STATUS_CAPTURED)
    if not no_capturadas.exists():
        for individual in individuals.all():
            send_email_client_payment_captured(individual.client, individual, \
                    subject='Tu Compra fue completada!')

def capture_payments_purchase(purchase):
    """
        Captura los Payments de la Completed Purchase que aun
        no han sido capturados
    """
    individuals = purchase.individuals_purchases
    individuals_sin_capturar = individuals.exclude(
                payment__status=PAYMENT_STATUS_CAPTURED)
    
    for individual in individuals_sin_capturar:
        payment_i = individual.payment
        res, ok = capture_payment(payment_i)
        if not ok:
            logger.error('no fue posible capturar el pago de la purchase {}: {}'.
                format(purchase.id, res))

def capture_payment(payment):
    res, ok = mercadopago.MercadoPagoPaymentService.capture(
        purch_id=payment.vendor_payment_id,
    )
    if ok:
        payment.set_status_captured()
    return (res, ok)

def cancel_payment(payment):
    res, ok = mercadopago.MercadoPagoPaymentService.cancel(
        purch_id=payment.vendor_payment_id,
    )
    if ok:
        payment.set_status_cancelled()
        send_email_client_payment_cancelled(payment.individual_purchase.client, payment.individual_purchase, 'Compra cancelada')
    return (res, ok)    

def update_shipment_status(sender, **kwargs):
    """
        Actualiza el estado del envio segun el estado
        del payment
    """
    payment = kwargs['instance']
    
    if payment.is_captured:
        shipment = payment.individual_purchase.shipment
        shipment.set_status_pending()

    if payment.is_reserved:
        shipment = payment.individual_purchase.shipment
        shipment.set_status_awaiting_purchase_completition()

    if payment.is_cancelled:
        shipment = payment.individual_purchase.shipment
        shipment.set_status_aborted()        


def cancel_payments(purchase):
    
    individuals = purchase.individuals_purchases

    for individual in individuals.all():
        cancel_payment(individual.payment)


def shipment_status_notify_client(sender, **kwargs):
    shipment = kwargs['instance']

    if shipment.dispatched:
        individual = shipment.individual_purchase
        purchase = individual.purchase
        client = individual.client 
        link = '{}{}'.format(settings.BASE_URL_PAGE_SHIPMENT_STATUS, shipment.id)
        data_ctx = {
            'client_firstname': client.first_name,
            'client_lasttname': client.last_name,
            'link': link,
            'address': individual.shipment.human_readable_address,
            'status': 'En camino'
        }
        send_email_purchase('Estado compra', client.email, data_ctx)
        return

    if shipment.delivered:
        individual = shipment.individual_purchase
        purchase = individual.purchase
        client = individual.client 
        link = '{}{}'.format(settings.BASE_URL_PAGE_SHIPMENT_STATUS, shipment.id)
        data_ctx = {
            'client_firstname': client.first_name,
            'client_lasttname': client.last_name,
            'link': link,
            'address': individual.shipment.human_readable_address,
            'status': 'Entregado'
        }
        send_email_purchase('Estado compra', client.email, data_ctx)
        return


def send_email_client_payment_captured(client, individual, subject, message=''):
    shipment = individual.shipment
    link = '{}{}'.format(settings.BASE_URL_PAGE_SHIPMENT_STATUS, shipment.id)
    data_ctx = {
        'client_firstname': client.first_name,
        'client_lasttname': client.last_name,
        'link': link,
        'address': individual.shipment,
        'status': 'Preparandose'
    }    
    sent = send_email_purchase('Pago realizado', client.email, data_ctx)
    if sent == 0:
        logger.error('no fue posible enviar el mail a {}'.\
            format(client.emal))



def send_email_client_payment_cancelled(client, individual, subject, message=''):
    shipment = individual.shipment
    link = '{}{}'.format(settings.BASE_URL_PAGE_SHIPMENT_STATUS, shipment.id)
    data_ctx = {
        'client_firstname': client.first_name,
        'client_lasttname': client.last_name,
        'link': link,
        'address': individual.shipment,
        'status': 'Cancelado'
    }    
    sent = send_email_purchase(subject, client.email, data_ctx)
    if sent == 0:
        logger.error('no fue posible enviar el mail a {}'.\
            format(client.emal))
