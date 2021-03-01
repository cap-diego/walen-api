# From django
from django.urls import path

# From w
from purchases.views import create_purchase_view, \
    get_purchase_view, create_individual_purchase_view, \
        list_individual_purchase_view, detail_payment_view, \
            detail_shipment_view,  create_payment_view

urlpatterns = [
    path('',  create_purchase_view, name='purchase-list'),
    
    path('<uuid:purchase_id>',  get_purchase_view, \
        name='purchase-detail'),
    
    path('<uuid:purchase_id>/individuals', \
        create_individual_purchase_view, \
        name='individual-purchase-list'),

    path('individuals/<uuid:ind_purch_id>',
        list_individual_purchase_view,
        name='individual-purchase-detail' ),

    path('payments/<uuid:payment_id>',
        detail_payment_view,
        name='payment-detail'),
    
    path('shipments/<uuid:shipment_id>',
        detail_shipment_view,
        name='shipment-detail'),

    path('payments/<uuid:payment_id>/vendor',
        create_payment_view,
        name='payment-vendor-detail')
]