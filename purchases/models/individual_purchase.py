# From django 
from django.db import models

# Utils 
import uuid

from purchases.models.purchase import Purchase
from purchases.models.payment import create_payment
from purchases.models.shipment import create_shipment

class IndividualPurchase(models.Model):
    
    id = models.UUIDField(primary_key=True, \
            default=uuid.uuid4, editable=False, \
            verbose_name='Individual purchase id' )
    
    client = models.ForeignKey(to='users.Client',
                                on_delete=models.CASCADE,
                                related_name="individuals_purchases")

    purchase = models.ForeignKey(to=Purchase,
                                    on_delete=models.CASCADE,
                                    related_name='individuals_purchases')
    
    shipment = models.OneToOneField(to='purchases.Shipment',
                                    on_delete=models.CASCADE,
                                    related_name='individual_purchase')

    payment = models.OneToOneField(to='purchases.Payment',
                                    on_delete=models.CASCADE,
                                    related_name='individual_purchase')

    creation_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creation_date']
        indexes = [
            models.Index(fields=['client'], name='client_idx'),
        ]


def create_individual_purchase(purchase, client, addr):
    client_already = IndividualPurchase.objects.filter(
        client=client,
        purchase=purchase
    )
    
    if client_already.exists():
        return None, 'error, client cant buy twice in the same purchase'
    
    try:
        individual = IndividualPurchase.objects.create(
            client=client,
            purchase=purchase,
            shipment=create_shipment(addr),
            payment=create_payment()
        )
    except Exception as err:
        return None, '{}'.format(err)
    return individual, ''



def purchase_history(client, last=10):
    qs = IndividualPurchase.objects.filter(
        client=client
    )
    return qs[:last]

