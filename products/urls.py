# From django
from django.urls import path, include

# From drf 
from rest_framework import routers

# From w
from products import views
from products.views import ProductViewSet, CategoryViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'', ProductViewSet)

urlpatterns = router.urls