# From django
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

# From drf
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status

# From w 
from users.serializers import UserSerializer, ClientProfileSerializer
from users.auth import magiclink
from users.auth.utils import did_token_required, \
    email_in_url_required
from users.models import Client, create_client

User = get_user_model()


@api_view(['POST'])
@permission_classes([])
@did_token_required
def create_cliente_view(request):
    data, err = parse_req_body_to_user_data(request.data)
    if err:
        return Response('error parsing body: {}'.format(err), \
            status=status.HTTP_400_BAD_REQUEST)
    try:
        client, err = create_client(data)
    except IntegrityError:
        return Response('error creating client', \
            status=status.HTTP_400_BAD_REQUEST)
    if err:
        return Response(err, status=status.HTTP_400_BAD_REQUEST)
    serializer = ClientProfileSerializer(client)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([])
@email_in_url_required
def cliente_exists_view(request, email):
    cliente = Client.objects.filter(email=email)
    if not cliente.exists():
        return Response({'description': 'email not registered'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'description': 'ok'})


def parse_req_body_to_user_data(body):
    data = {}
    data['email'] = body['email']
    if not email_is_valid(data['email']):
        return None, 'error, email is invalid'
    data['username'] = data['email']
    if body.get('first_name', None):
        data['first_name'] = body.get('first_name', None)
    if body.get('last_name', None):
        data['last_name'] = body.get('last_name', None)
    return data, None

def email_is_valid(email):
    import re 
    return re.fullmatch('[^@]+@[^@]+\.[^@]+', email)


@api_view(['GET'])
@permission_classes([])
@did_token_required
@email_in_url_required
def cliente_profile_view(request, email):
    client = get_object_or_404(Client, email=email)
    serializer = ClientProfileSerializer(client)
    return Response(serializer.data, status=status.HTTP_200_OK)

