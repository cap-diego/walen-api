# From django
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)


class Client(models.Model):

    user = models.OneToOneField(to='users.User', \
                                on_delete=models.SET_NULL,
                                null=True
                                )   

    # address = models.ForeignKey(to='users.Address',
    #                             on_delete=models.CASCADE,
    #                             related_name="client")

class Address(models.Model):
    commentary = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=60)
    floor_apt = models.CharField(max_length=15)
    address_line = models.CharField(max_length=50)
    country = models.CharField(max_length=30)
    geocoding = models.OneToOneField(to='users.AddressGeoCodingResult',
                                    null=True,
                                    on_delete=models.SET_NULL)
class AddressGeoCodingResult(models.Model):
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    label = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    geocoding_result_type = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    street = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=10)
    confidence = models.PositiveSmallIntegerField()
    region = models.CharField(max_length=100)
    region_code = models.CharField(max_length=15)
    administrative_area = models.CharField(max_length=40)
    neighbourhood = models.CharField(max_length=40)
    country = models.CharField(max_length=50)
    country_code = models.CharField(max_length=30)
    map_url = models.URLField()

