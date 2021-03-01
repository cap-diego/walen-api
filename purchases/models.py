# From django 
from django.db import models
from django.core.exceptions import ValidationError

# Utils 
import uuid
from datetime import timedelta

# From w
from purchases.constants import PURCHASE_STATUS_CHOICES, \
    PURCHASE_STATUS_PEND_INIT_PAY, PAYMENT_STATUS_CHOICES, \
        PAYMENT_STATUS_PENDING, SHIPMENT_STATUS_CHOICES, \
            SHIPMENT_STATUS_PENDING
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
    
    discount_amount = models.PositiveSmallIntegerField(default=0)

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
        return super().clean()
    
    def validate_confirmed_clients(self):
        if self.current_confirmed_clients > self.clients_target:
            raise ValidationError('error, purchase already reached clients target')
    
    def add_confirmed_client(self):
        self.current_confirmed_clients += 1
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
    def amount_to_pay(self):
        return self.cart_price - self.discount_amount

    @property
    def shipment_area_radius(self):
        """ represents the max distance to 
            delivery a groupal purchase
        """
        return 20
    
    @property
    def expiration_date(self):
        return self.creation_date + timedelta(days=1)


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
                                    on_delete=models.CASCADE)

    payment = models.OneToOneField(to='purchases.Payment',
                                    on_delete=models.CASCADE)

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


class Shipment(models.Model):

    id = models.UUIDField(primary_key=True, \
        default=uuid.uuid4, editable=False, \
        verbose_name='Shipment id' )
    
    status = models.CharField(choices=SHIPMENT_STATUS_CHOICES,
                                default=SHIPMENT_STATUS_PENDING,
                                max_length=3)


    shipment_address = models.ForeignKey(to=Address,
                                            on_delete=models.CASCADE,
                                            related_name='shipments')
           

def create_payment():
    return Payment.objects.create()

def create_shipment(addr):
    return Shipment.objects.create(shipment_address=addr)

def create_individual_purchase(purchase, client, addr):
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