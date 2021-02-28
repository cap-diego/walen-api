# From django 
from django.db import models
from django.core.exceptions import ValidationError

# Utils 
import uuid

# From w
from purchases.constants import PURCHASE_STATUS_CHOICES, \
    PURCHASE_STATUS_PEND_INIT_PAY
from carts.models import Cart 
from users.models import Address

class Purchase(models.Model):
    id = models.UUIDField(primary_key=True, \
            default=uuid.uuid4, editable=False, \
            verbose_name='Cart id' )

    creation_date = models.DateTimeField(auto_now=True)

    expiration_date = models.DateTimeField(auto_now_add=True)

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
            raise ValidationError('error, clients confirmed is greater than clients target')
    
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