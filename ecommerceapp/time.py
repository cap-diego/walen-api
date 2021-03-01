# From django
from django.utils import timezone

class APIClock:

    @staticmethod
    def date_is_expired(date_to_compare):
        now = timezone.now()
        return date_to_compare < now
    
    @staticmethod
    def now():
        return timezone.now()
