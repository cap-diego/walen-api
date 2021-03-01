# From django
from django.test import TestCase

# Utils
from datetime import timedelta

# From w
from ecommerceapp import time

class APIClockTestCase(TestCase):

    def test_tomorrow_is_not_expired(self):

        tomorrow = time.APIClock.now() + timedelta(days = 1)

        assert not time.APIClock.date_is_expired(tomorrow)

    def test_yesterday_is_expired(self):
        
        yesterday = time.APIClock.now() - timedelta(days = 1)

        assert time.APIClock.date_is_expired(yesterday)



