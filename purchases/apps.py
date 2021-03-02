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
        post_save.connect(signals.update_purchase_related_models_status, \
                sender='purchases.Purchase', \
                dispatch_uid=uuid.uuid4())

        post_save.connect(signals.update_shipment_status, \
                sender='purchases.Payment', \
                dispatch_uid=uuid.uuid4())

        post_save.connect(signals.shipment_status_notify_client, \
                sender='purchases.Shipment', \
                dispatch_uid=uuid.uuid4())