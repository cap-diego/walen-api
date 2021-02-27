# From django
from django.db import models
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Utils 
import uuid

# From w
from products.models import Product


class Cart(models.Model):

    id = models.UUIDField(primary_key=True, \
        default=uuid.uuid4, editable=False, \
        verbose_name='Cart id' )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    locked = models.BooleanField(default=False)
    products  = models.ManyToManyField(to=Product, \
        related_name='carts',
        through='CartProduct')

    @property 
    def is_locked(self):
        return self.locked

    @property
    def is_empty(self):
        return self.products.count() == 0

    @property
    def total(self):
        """ total returns de total amount to pay """
        cart_prods = CartProduct.objects.filter(cart=self)
        def calc_amount_of_product(prod, qt):
            return prod*qt
        mount_by_product = map(lambda cart_prod: \
                calc_amount_of_product(cart_prod.count, \
                    cart_prod.product.unitary_price), \
                cart_prods
            )
        total = sum(mount_by_product)
        return total

    def get_cartprod(self, prod):
        return CartProduct.objects.filter(
                        cart=self, product=prod)

    def create_cartprod(self, prod, qt):
        return CartProduct.objects.create(
            cart=self,
            count=qt, 
            product=prod
        )

    def add(self, prod, qt):
        """ add updates the cart and returns 1 if succ or 0 otherwise"""
        if self.is_locked:
            return 0
        if qt < 0: 
            return 0
        cart_prod = self.get_cartprod(prod)
        if cart_prod.exists():
            if qt == 0:
                cart_prod.delete()
            else:
                cart_prod.update(count=qt)
        else:
            try:
                self.create_cartprod(prod, qt)
            except IntegrityError as e:
                return 0
        return 1

    def lock(self):
        if self.is_empty:
            return 0
        self.locked = True
        self.save()

class CartProduct(models.Model):
    cart = models.ForeignKey(to=Cart, \
        on_delete=models.CASCADE)

    product = models.ForeignKey(to=Product, \
        on_delete=models.CASCADE)

    count = models.PositiveSmallIntegerField()