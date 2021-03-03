# From Magic.Link
import magic_admin
from magic_admin.error import DIDTokenError
from magic_admin.error import RequestError

# From drf
from rest_framework.response import Response
from rest_framework import status

# Utils
from functools import wraps

# From w
from users.auth import magiclink

def did_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request = args[0]
        email = request.data.get('email', None)
        
        if not email:
            email = kwargs.get('email', None)
        
        if not email:
            return Response('error, email expected', \
                status=status.HTTP_400_BAD_REQUEST)
        
        did_token = request.headers.get('Authorization', None)

        if did_token is None:
            error_message = 'error, expected token'
            return Response(error_message, \
                status=status.HTTP_400_BAD_REQUEST)

        magic = magiclink.MagicLinkAuth()
        valid, err = magic.didtoken_is_valid(did_token, email)
        if not valid:
            error_message = '{}'.format(err)
            return Response(error_message, \
                status=status.HTTP_400_BAD_REQUEST)

        return f(*args, **kwargs)
    return decorated_function


def email_in_url_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        email = kwargs.get('email', None)
        if email is None:
            error_message = 'error, expected email'
            return Response(error_message, \
                status=status.HTTP_400_BAD_REQUEST)

        if not email_is_valid(email):
            error_message = 'error, email {} is invalid'.format(email)
            return Response(error_message, \
                status=status.HTTP_400_BAD_REQUEST)
        return f(*args, **kwargs)
    return decorated_function

def email_is_valid(email):
    import re 
    return re.fullmatch('[^@]+@[^@]+\.[^@]+', email)
