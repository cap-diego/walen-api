# From django 
from django.apps import AppConfig
from django.db.models.signals import post_save

# Utils 
import uuid

# From w 
from purchases import signals

class PurchasesConfig(AppConfig):
    name = 'purchases'

    def ready(self):
        post_save.connect(signals.check_if_purchase_finished, \
                sender='purchases.Purchase', \
                dispatch_uid=uuid.uuid4())

        post_save.connect(signals.check_if_shipment_staus_should_be_pending, \
                sender='purchases.Payment', \
                dispatch_uid=uuid.uuid4())