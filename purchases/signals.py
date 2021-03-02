from django.db import transaction

from purchases.payment_vendors import mercadopago
from purchases.constants import PAYMENT_STATUS_CAPTURED

def update_purchase_related_models_status(sender, **kwargs):
    purchase = kwargs['instance']

    if purchase.is_cancelled:
        abort_shipments(purchase)
        return

    if purchase.is_completed:
        capture_payments(purchase)
        return

    if not purchase.clients_target_reached:
        return
    
    purchase.set_status_completed()

    

def capture_payments(purchase):
    
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