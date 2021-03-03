
# From django 
from django.db import models
from django.core.exceptions import ValidationError

# Utils 
import uuid
from datetime import timedelta

# From w
from purchases.constants import PURCHASE_STATUS_CHOICES, \
    PURCHASE_STATUS_PEND_INIT_PAY, PURCHASE_STATUS_COMPLETED,  \
    PURCHASE_STATUS_AWAITING_PEERS, PURCHASE_STATUS_CANCELLED

from carts.models import Cart

from users.models import Address

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


def purchase_recommendations(client):
    """
        Recomendar los productos que resulten de:
            comprados por personas que han participado en compras grupales con el usuario
    """
    lasts_groupal_purchases = Purchase.objects.filter(
        clients_target__gt=1, #colaborativa
        individuals_purchases__client=client, # participo cliente
    )[:5]

    products = []
    for purchase in lasts_groupal_purchases.all():
        if products == []:
            products = purchase.cart.products.all() 
        else:
            products = products.union(purchase.cart.products.all())
    
    return products