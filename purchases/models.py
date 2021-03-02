# From django 
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, \
    MaxValueValidator

# Utils 
import uuid
from datetime import timedelta

# From w
from purchases.constants import PURCHASE_STATUS_CHOICES, \
    PURCHASE_STATUS_PEND_INIT_PAY, PAYMENT_STATUS_CHOICES, \
    PAYMENT_STATUS_PENDING, SHIPMENT_STATUS_CHOICES, \
    SHIPMENT_STATUS_AWAITING_PAYMENT, \
    PAYMENT_VENDOR_CHOICES, PAYMENT_STATUS_RESERVED, \
    PAYMENT_STATUS_FAILED, PURCHASE_STATUS_AWAITING_PEERS, \
    PURCHASE_STATUS_COMPLETED, PAYMENT_STATUS_CAPTURED, \
    SHIPMENT_STATUS_PENDING, SHIPMENT_STATUS_ABORTED, \
    SHIPMENT_STATUS_AWAITING_PURCHASE_COMPLETITION, \
    PURCHASE_STATUS_CANCELLED, SHIPMENT_STATUS_DISPATCHED, \
    SHIPMENT_STATUS_DELIVERED

from carts.models import Cart 
from users.models import Address
from users.serializers import AddressSerializer

class Purchase(models.Model):
    
    id = models.UUIDField(primary_key=True, \
            default=uuid.uuid4, editable=False, \
            verbose_name='Purchase id' )

    creation_date = models.DateTimeField(auto_now=True)

    status = models.CharField(choices=PURCHASE_STATUS_CHOICES,
                                max_length=3,
                                default=PURCHASE_STATUS_PEND_INIT_PAY)

    clients_target = models.PositiveSmallIntegerField()
    
    current_confirmed_clients = models.PositiveSmallIntegerField(default=0)


    cart = models.ForeignKey(  to=Cart, \
                                on_delete=models.CASCADE,
                                related_name='purchases')
    
    shipment_area_center = models.ForeignKey(to=Address,
                                            on_delete=models.CASCADE,
                                            related_name='purchases')

    class Meta:
        ordering = ['-creation_date']

    def save(self, *args, **kwarsg):
        self.clean()
        return super().save()

    def clean(self):
        self.validate_confirmed_clients()
        self.validate_clients_target_is_not_zero()
        return super().clean()
    
    def validate_clients_target_is_not_zero(self):
        if self.clients_target == 0:
            raise ValidationError('error, clients target cant be zero')
        
    def validate_confirmed_clients(self):
        if self.current_confirmed_clients > self.clients_target:
            raise ValidationError('error, purchase already reached clients target')
    
    def add_confirmed_client(self):
        self.current_confirmed_clients += 1
        self.save()

    def set_status_awaiting_peers(self):
        self.status = PURCHASE_STATUS_AWAITING_PEERS
        self.save()

    def set_status_completed(self):
        self.status = PURCHASE_STATUS_COMPLETED
        self.save()      

    def set_status_cancelled(self):
        if self.is_completed:
            raise ValidationError('error, completed purchase cant be cancelled')
        self.status = PURCHASE_STATUS_CANCELLED
        self.save()  

    @property
    def clients_left(self): 
        return self.clients_target - self.current_confirmed_clients

    @property
    def clients_target_reached(self):
        return self.clients_left == 0
    
    @property
    def cart_price(self):
        return self.cart.total

    @property 
    def amount(self):
        return self.cart_price - self.discount_amount
    
    @property
    def discount_amount(self):
        return (self.clients_target - 1) * 0.1 * self.cart_price

    @property
    def shipment_area_radius(self):
        """ represents the max distance to 
            delivery a groupal purchase
        """
        return 20
    
    @property
    def expiration_date(self):
        return self.creation_date + timedelta(days=1)
    
    @property
    def is_completed(self):
        return self.status == PURCHASE_STATUS_COMPLETED
    
    @property
    def is_cancelled(self):
        return self.status == PURCHASE_STATUS_CANCELLED

    @property
    def amount(self):
        return self.cart_price - self.discount_amount

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

def create_payment():
    return Payment.objects.create()

def create_shipment(addr):
    return Shipment.objects.create(shipment_address=addr)

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

def get_or_create_addr(addr):
    if addr is None:
        return None, ''

    serializer = AddressSerializer(data=addr)
    if not serializer.is_valid():
        return None, '{}'.format(serializer.errors)
    try:
        addr = serializer.save()
    except Exception as err:
        return None, 'error creating Address:  [{}]'.format(err)

    return addr, ''


class Coupon(models.Model):

    id = models.UUIDField(primary_key=True, \
        default=uuid.uuid4, editable=False, \
        verbose_name='Coupon id' )

    discount_percent = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0, 'error, el porcentaje no puede ser inferior a 0'), \
            MaxValueValidator(99, 'error, el porcentaje no puede superar 99')]
    )

    def __str__(self):
        return 'Cupon de {}% de descuento'.format(self.discount_percent)
    