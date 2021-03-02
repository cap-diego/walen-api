from django.db import transaction
from django.core import mail
from django.conf import settings

from purchases.payment_vendors import mercadopago
from purchases.constants import PAYMENT_STATUS_CAPTURED

def update_purchase_related_models_status(sender, **kwargs):
    purchase = kwargs['instance']

    if purchase.is_cancelled:
        abort_shipments(purchase)
        return

    if purchase.is_completed:
        capture_payments(purchase)
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
            send_email_client(individual.client, \
                    subject='Tu Compra fue completada!')

def send_email_client(client, subject):
    platform_email = settings.PLATFORM_EMAIL
    mail.send_mail(
        subject, '',
        platform_email, [client.email],
        fail_silently=False,
    )


def capture_payments(purchase):
    """
        Captura los Payments de la Completed Purchase que aun
        no han sido capturados
    """
    individuals = purchase.individuals_purchases
    individuals_sin_capturar = individuals.exclude(
                payment__status=PAYMENT_STATUS_CAPTURED)
    
    for individual in individuals_sin_capturar:
        payment_i = individual.payment
        res, ok = mercadopago.MercadoPagoPaymentService.capture(
            purch_id=payment_i.vendor_payment_id,
        )

        if ok:
            payment_i.set_status_captured()
        

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


def abort_shipments(purchase):
    
    individuals = purchase.individuals_purchases

    for individual in individuals.all():
        individual.shipment.set_status_aborted()


def shipment_status_notify_client(sender, **kwargs):
    shipment = kwargs['instance']

    if shipment.dispatched:
        individual = shipment.individual_purchase
        purchase = individual.purchase
        client = individual.client 
        send_email_client(client, \
                subject='Purchase {} está en camino!'.format(purchase.id))
        return

    if shipment.delivered:
        individual = shipment.individual_purchase
        purchase = individual.purchase
        client = individual.client 
        send_email_client(client, \
                subject='Purchase {} fue entregada! Que la disfrutes!'.format(purchase.id))
        return