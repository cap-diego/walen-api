# From django
from django.urls import path

# From w 
from users.views import get_user, new, user_profile_view

urlpatterns = [
    path('profile/<str:email>', user_profile_view),
    path('<str:email>', get_user),
    path('new/', new),
]
