# From django 
from django.db import models

# Utils 
import uuid


from purchases.constants import SHIPMENT_STATUS_ABORTED, SHIPMENT_STATUS_CHOICES, \
    SHIPMENT_STATUS_AWAITING_PURCHASE_COMPLETITION, SHIPMENT_STATUS_AWAITING_PAYMENT, \
    SHIPMENT_STATUS_PENDING, SHIPMENT_STATUS_DISPATCHED, SHIPMENT_STATUS_DELIVERED

from users.models import Address

class Shipment(models.Model):

    id = models.UUIDField(primary_key=True, \
        default=uuid.uuid4, editable=False, \
        verbose_name='Shipment id' )
    
    status = models.CharField(choices=SHIPMENT_STATUS_CHOICES,
                                default=SHIPMENT_STATUS_AWAITING_PAYMENT,
                                max_length=3)


    shipment_address = models.ForeignKey(to=Address,
                                            on_delete=models.CASCADE,
                                            related_name='shipments')

    def __str__(self):
        return 'Shipment {} [{}]'.format(self.id, self.get_status_display())

    def set_status_pending(self):
        self.status = SHIPMENT_STATUS_PENDING
        self.save()
    
    def set_status_awaiting_purchase_completition(self):
        self.status = SHIPMENT_STATUS_AWAITING_PURCHASE_COMPLETITION
        self.save()

    def set_status_aborted(self):
        self.status = SHIPMENT_STATUS_ABORTED
        self.save()

    def set_status_dispatched(self):
        self.status = SHIPMENT_STATUS_DISPATCHED
        self.save()

    def set_status_delivered(self):
        self.status = SHIPMENT_STATUS_DELIVERED
        self.save()

    @property
    def is_pending(self):
        return self.status == SHIPMENT_STATUS_PENDING

    @property
    def is_awaiting_purchase_completition(self):
        return self.status == SHIPMENT_STATUS_AWAITING_PURCHASE_COMPLETITION
    
    @property
    def is_aborted(self):
        return self.status == SHIPMENT_STATUS_ABORTED

    @property
    def dispatched(self):
        return self.status == SHIPMENT_STATUS_DISPATCHED

    @property
    def delivered(self):
     return self.status == SHIPMENT_STATUS_DELIVERED

    @property
    def individual_purchase_id(self):
        return self.individual_purchase.id
    
    @property
    def human_readable_address(self):
        return self.shipment_address

def create_shipment(addr):
    return Shipment.objects.create(shipment_address=addr)