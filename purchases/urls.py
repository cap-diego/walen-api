# From django
from django.urls import path

# From w
from purchases.views import create_purchase_view, \
    get_purchase_view, create_individual_purchase_view, \
    list_individual_purchase_view, detail_payment_view, \
    detail_shipment_view, create_payment_view, cancel_puchase_view, \
    payment_add_coupon_view, coupons_list_view, purchase_history_view, \
    purchase_recommendations_view

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
        name='payment-vendor-detail'),

    path('<uuid:purchase_id>/cancel',
        cancel_puchase_view,
        name='purchase-cancel'),

    path('payments/<uuid:payment_id>/coupon',
        payment_add_coupon_view,
        name='payment-coupon'),

    path('payments/coupon',
        coupons_list_view,
        name='coupon-list'),
        
    path('<str:email>/history', purchase_history_view,
        name='client-purchases-history'),

    path('<str:email>/recommendations', purchase_recommendations_view,
        name='client-recommendatios')
]