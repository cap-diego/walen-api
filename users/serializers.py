
# From django
from django.contrib.auth import get_user_model

# From drf
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'last_name', 'date_joined', 'last_login']
