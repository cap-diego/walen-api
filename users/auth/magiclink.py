# From django
from django.conf import settings

# utils
from magic_admin import Magic
from magic_admin.error import DIDTokenError
from magic_admin.error import RequestError

class MagicLinkAuth:
    
    def __init__(self):
        self.magic = self._create_magic_link()

    def _create_magic_link(self):
        return Magic(
            api_secret_key=settings.MAGIC_LINK_SECRET_KEY,
            retries=5,
            timeout=5,
            backoff_factor=0.01,
        )


    def didtoken_is_valid(self, didtoken, email):
        try:
            self.magic.Token.validate(didtoken)
            issuer = self.magic.Token.get_issuer(didtoken)
        except DIDTokenError as e:
            return False, 'didtoken invalid'
        
        if not email:
            return True, None 

        coincide, err = self._email_coincide_with_token(didtoken, email)
        if not coincide:
            return False, err

        return True, None

    def _email_coincide_with_token(self, didtoken, email):
        try:
            magic_response = self.magic.User.get_metadata_by_token(didtoken)
        except RequestError as e:
            return False, 'error verifying email and token: {}'.format(e)

        if magic_response.data['email'] != email:
            return False, 'error, email not coincide with token'

        return True, ''