# From django
from django.urls import path

# From w 
from users.views import user_exists_view, create_user_view, user_profile_view

urlpatterns = [
    path('profile/<str:email>', user_profile_view,
        name='user-profile'),

    path('<str:email>', user_exists_view,
        name='user-exists'),

    path('new/', create_user_view,
        name='user-create'),
]
