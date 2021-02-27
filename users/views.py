# From django
from django.http import HttpResponse,  HttpResponseNotFound, HttpResponseBadRequest
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods

# From drf
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

# utils 
import json

# From w 
from users.serializers import UserSerializer
from users.auth import magiclink

User = get_user_model()
APPLICATION_JSON = 'application/json'

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]       

    @action(detail=False, methods=['POST'], permission_classes=[])
    def new(self, request):
        token = request.headers.get('Authorization', None)
        body = request.data
        email = body.get('email', None)
        if not token:
            return Response('error, expected token', status=status.HTTP_400_BAD_REQUEST)
        
        if not email_is_valid(email):
            return Response('error, expected email or is invalid', status=status.HTTP_400_BAD_REQUEST)
        
        magic = magiclink.MagicLinkAuth()
        res, err = magic.didtoken_is_valid(token, email)
        if not res:
            return Response(err, status=status.HTTP_400_BAD_REQUEST)
        user, err = create_user(body)
        if err:
            return Response(err, status=status.HTTP_400_BAD_REQUEST)
        user_serialized = UserSerializer(user).data
        return Response(user_serialized, status=status.HTTP_201_CREATED)

@require_http_methods(['GET'])
def get_user(request, email):
    if not email_is_valid(email):
        error_msj = json.dumps({'description': 'email invalid'})
        return HttpResponseBadRequest(error_msj, content_type=APPLICATION_JSON)
    users = User.objects.filter(email=email)
    if not users.exists():
        error_msj = json.dumps({'description': 'user does not exists'})
        return HttpResponseNotFound(error_msj, content_type=APPLICATION_JSON)
    return HttpResponse('ok')

def email_is_valid(email):
    import re 
    return re.fullmatch('[^@]+@[^@]+\.[^@]+', email)

def create_user(body):
    data = parse_req_body_to_user_data(body)
    serializer = UserSerializer(data=data)
    if not serializer.is_valid():
        return None, 'error creating user'
    user = serializer.save()
    return user, None

def parse_req_body_to_user_data(body):
    data = {}
    data['email'] = body['email']
    data['username'] = data['email']
    if body.get('first_name', None):
        data['first_name'] = body.get('first_name', None)
    if body.get('last_name', None):
        data['last_name'] = body.get('last_name', None)
    return data
