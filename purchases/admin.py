from django.contrib import admin

from purchases.models import Shipment

class ShipmentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Shipment, ShipmentAdmin)