# From drf 
from rest_framework import routers

# From w 
from carts.views import CartViewSet


router = routers.DefaultRouter()
router.register(r'', CartViewSet)

urlpatterns = router.urls