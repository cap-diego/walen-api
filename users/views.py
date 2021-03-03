# From django
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

# From drf
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status

# From w 
from users.serializers import UserSerializer, ClientSerializer
from users.auth import magiclink
from users.auth.utils import did_token_required, \
    email_in_url_required
from users.models import Client, create_client

User = get_user_model()


@api_view(['POST', 'PUT'])
@permission_classes([])
@did_token_required
def create_or_update_cliente_view(request):
    email = request.data.get('email', None)
    if not email:
        return Response('error parsing body: email expected', \
            status=status.HTTP_400_BAD_REQUEST)
    
    clients_filtered = Client.objects.filter(email=email)
    
    if clients_filtered.exists():
        if request.method.upper() == 'POST':
            return Response('error, {} already registered'.format(email), \
                status=status.HTTP_400_BAD_REQUEST)

        serializer = ClientSerializer(clients_filtered.first(), \
                 data=request.data)
    else:
        serializer = ClientSerializer(data=request.data)
    
    ok = serializer.is_valid()
    
    if not ok:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    try:
        instance = serializer.save()
    except Exception as err:
        return Response('error creating client: {}'.format(err), \
            status=status.HTTP_400_BAD_REQUEST)
        
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([])
@email_in_url_required
def cliente_exists_view(request, email):
    cliente = Client.objects.filter(email=email)
    if not cliente.exists():
        return Response({'description': 'email not registered'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'description': 'ok'})

@api_view(['GET'])
@permission_classes([])
@did_token_required
@email_in_url_required
def cliente_profile_view(request, email):
    client = get_object_or_404(Client, email=email)
    serializer = ClientSerializer(client)
    return Response(serializer.data, status=status.HTTP_200_OK)

