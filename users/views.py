# From django
from django.contrib.auth import get_user_model

# From drf
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status

# From w 
from users.serializers import UserSerializer
from users.auth import magiclink

User = get_user_model()

@api_view(['POST'])
@permission_classes([])
def new(request):
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


@api_view(['GET'])
@permission_classes([])
def get_user(request, email):
    if not email_is_valid(email):
        return Response({'description': 'email invalid'}, status=status.HTTP_400_BAD_REQUEST)
    users = User.objects.filter(email=email)
    if not users.exists():
        return Response({'description': 'email not registered'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'description': 'ok'})

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
