# From django
from django.urls import path

# From w 
from users.views import get_user, new

urlpatterns = [
    path('<str:email>', get_user),
    path('new/', new)
]
