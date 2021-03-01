# From django
from django.test import TestCase
from django.test import Client as ClientReq
from django.contrib.auth import get_user_model

# From drf 
from rest_framework.reverse import reverse

# From w
from users.models import Client

# Utils
from unittest.mock import patch, MagicMock

# From ddf
from ddf import G


User = get_user_model()

class UsersTestCase(TestCase):

    @patch('users.auth.magiclink.MagicLinkAuth')
    def test_crear_usuario_con_token_valido(self, mock):
        _mock = MagicMock()
        _mock.didtoken_is_valid = MagicMock(return_value = (True, ''))
        mock.return_value = _mock
        c = ClientReq()
        data = {'email': 'Juancito@gmail.com'}
        url = reverse('user-create')
        response = c.post(url, data, HTTP_AUTHORIZATION='un token')
        assert response.status_code == 201
        assert response.json()['email'] == response.json()['user']['username']
        assert response.json()['email'] == data['email']

    def test_error_si_no_se_envia_token(self):
        c = ClientReq()
        data = {'email': 'Juancito@gmail.com'}
        url = reverse('user-create')
        response = c.post(url, data)
        assert response.status_code == 400
        assert response.json() == 'error, expected token'

    @patch('users.auth.magiclink.MagicLinkAuth')
    def test_error_si_token_no_es_valido(self, mock):
        _mock = MagicMock()
        reason_invalid = 'token es invalido'
        _mock.didtoken_is_valid = MagicMock(return_value = (False, reason_invalid))
        mock.return_value = _mock
        c = ClientReq()
        data = {'email': 'Juancito@gmail.com'}
        url = reverse('user-create')
        response = c.post(url, data, HTTP_AUTHORIZATION='un token')
        assert response.status_code == 400
        assert response.json() == reason_invalid

    @patch('users.auth.magiclink.MagicLinkAuth')
    def test_error_si_ya_existe_el_cliente(self, mock):
        _mock = MagicMock()
        _mock.didtoken_is_valid = MagicMock(return_value = (True, ''))
        mock.return_value = _mock
        c = ClientReq()
        data = {'email': 'Juancito@gmail.com'}
        self.crear_cliente(c, data)
        url = reverse('user-create')
        response = c.post(url, data, HTTP_AUTHORIZATION='un token')
        assert response.status_code == 400
        assert response.json() == 'error, {} already registered'.format(data['email'])

    def crear_cliente(self, c, data):
        response = c.post('/api/v1/users/new/', data, HTTP_AUTHORIZATION='un token')
        assert response.status_code == 201

    @patch('users.auth.magiclink.MagicLinkAuth')
    def test_usuario_existe_por_mail(self, mock):
        c = ClientReq()
        _mock = MagicMock()
        reason_invalid = 'token es invalido'
        _mock.didtoken_is_valid = MagicMock(return_value = (True, reason_invalid))
        mock.return_value = _mock
        
        data = {'email': 'Juancito@gmail.com'}
        self.crear_cliente(c, data)
        url = reverse('user-exists', args=[data['email']])
        response = c.get(url)
        assert response.status_code == 200

    def test_usuario_no_existe_por_mail(self):
        c = ClientReq()
        email = 'Juancito@gmail.com'
        url = reverse('user-exists', args=[email])
        response = c.get(url)
        assert response.status_code == 404
