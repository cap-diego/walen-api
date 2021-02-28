# From django
from django.urls import path

# From w
from purchases.views import create_purchase, \
    get_purchase

urlpatterns = [
    path('',  create_purchase),
    path('<uuid:purchase_id>',  get_purchase)
]