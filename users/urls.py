# From django
from django.urls import path

# From drf
from rest_framework.routers import DefaultRouter

# From w 
from users.views import UserViewSet, get_user


router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('<str:email>', get_user),
]

urlpatterns += router.urls
