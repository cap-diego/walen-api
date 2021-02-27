"""ecommerceapp URL Configuration
"""

# From django
from django.contrib import admin
from django.urls import path, include

# From drf
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/products/', include('products.urls')),
    path('api/v1/users/', include('users.urls'))
]
