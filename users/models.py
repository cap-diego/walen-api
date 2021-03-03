# From django
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import transaction


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)


class Client(models.Model):

    email = models.EmailField(unique=True)

    first_name = models.CharField(blank=True, max_length=20)

    last_name = models.CharField(blank=True, max_length=20)

    avatar_url = models.URLField(blank=True)
    

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

    def __str__(self):
        return '{} {} (floor {})'.format(self.city, self.address_line, self.floor_apt)

class AddressGeoCodingResult(models.Model):
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    label = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    geocoding_result_type = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    street = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    confidence = models.PositiveSmallIntegerField(null=True)
    region = models.CharField(max_length=100)
    region_code = models.CharField(max_length=15)
    administrative_area = models.CharField(max_length=40, blank=True, null=True)
    neighbourhood = models.CharField(max_length=40, blank=True, null=True)
    country = models.CharField(max_length=50)
    country_code = models.CharField(max_length=30)
    map_url = models.URLField(blank=True)


def create_geocoding_result(data):
    try:
        return (AddressGeoCodingResult.objects.create(
            **data
        ), '')
    except Exception as err:
        return (None, '{}'.format(err))

def create_address(data):
    geo = data.pop('geocoding')
    if geo:
        geo, err = create_geocoding_result(geo)
        if err:
            return (None, '{}'.format(err))
    try:
        return (Address.objects.create(
            geocoding=geo,
            **data
        ), '')
    except Exception as err:
        return (None, '{}'.format(err))

def get_or_create_client(email):
    client, _ = Client.objects.get_or_create(email=email)
    return client

def create_client(data):
    email = data['email']
    clients = Client.objects.filter(email=email)
    if clients.exists():
        return None, 'error, {} already registered'.format(email)
    client = Client.objects.create(email=email)
    return client, ''

