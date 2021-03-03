
# From django 
from django.db import models

# Utils 
import uuid

from purchases.constants import PAYMENT_STATUS_CAPTURED, PAYMENT_STATUS_PENDING, \
    PAYMENT_STATUS_RESERVED, PAYMENT_STATUS_FAILED, PAYMENT_VENDOR_CHOICES, \
    PAYMENT_STATUS_CHOICES, PAYMENT_STATUS_CANCELLED

class Payment(models.Model):
    id = models.UUIDField(primary_key=True, \
        default=uuid.uuid4, editable=False, \
        verbose_name='Payment id' )
    
    status = models.CharField(choices=PAYMENT_STATUS_CHOICES,
                                default=PAYMENT_STATUS_PENDING,
                                max_length=3)

    vendor_payment_id = models.PositiveBigIntegerField(null=True)

    vendor_name = models.CharField(choices=PAYMENT_VENDOR_CHOICES,
                                    blank=True,
                                    max_length=15)

    coupon = models.ForeignKey('purchases.Coupon',
                                null=True,
                                on_delete=models.SET_NULL)

    def save_vendor_info(self, vendor_id, vendor_name):
        self.vendor_payment_id = vendor_id
        self.vendor_name = vendor_name
        self.save()
    
    def set_status_reserved(self):
        self.status = PAYMENT_STATUS_RESERVED
        self.save()

    def set_status_failed(self):
        self.status = PAYMENT_STATUS_FAILED
        self.save()
    
    def set_status_captured(self):
        self.status = PAYMENT_STATUS_CAPTURED
        self.save()

    def set_status_cancelled(self):
        self.status = PAYMENT_STATUS_CANCELLED
        self.save()

    def add_coupon(self, coupon):
        self.coupon = coupon
        self.save()

    @property
    def is_reserved(self):
        return self.status == PAYMENT_STATUS_RESERVED
    
    @property
    def failed(self):
        return self.status == PAYMENT_STATUS_FAILED

    @property
    def is_captured(self):
        return self.status == PAYMENT_STATUS_CAPTURED
    
    @property
    def individual_purchase_id(self):
        return self.individual_purchase.id

    @property
    def amount_to_pay(self):
        purchase = self.individual_purchase.purchase
        if self.has_coupon: 
            discount = purchase.amount * (self.coupon.discount_percent/100)
            return purchase.amount - discount
        return purchase.amount 

    @property
    def has_coupon(self):
        return self.coupon


def create_payment():
    return Payment.objects.create()