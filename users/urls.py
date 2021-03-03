# From django
from django.urls import path

# From w 
from users.views import cliente_exists_view, create_cliente_view, \
    cliente_profile_view

urlpatterns = [
    path('profile/<str:email>', cliente_profile_view,
        name='cliente-profile'),

    path('<str:email>', cliente_exists_view,
        name='cliente-exists'),

    path('new/', create_cliente_view,
        name='cliente-create'),
]
