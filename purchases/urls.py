# From django
from django.urls import path

# From w
from purchases.views import create_purchase, \
    get_purchase, create_individual

urlpatterns = [
    path('',  create_purchase, name='purchase-list'),
    path('<uuid:purchase_id>',  get_purchase, name='purchase-detail'),
    path('<uuid:purchase_id>/individual',  create_individual, name='purchase-individual'),
]