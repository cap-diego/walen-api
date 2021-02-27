# From django
from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model

# Utils
from unittest.mock import patch, MagicMock

User = get_user_model()

class UsersTestCase(TestCase):

    @patch('users.auth.magiclink.MagicLinkAuth')
    def test_crear_usuario_con_token_valido(self, mock):
        _mock = MagicMock()
        _mock.didtoken_is_valid = MagicMock(return_value = (True, ''))
        mock.return_value = _mock
        c = Client()
        data = {'email': 'Juancito@gmail.com'}
        response = c.post('/api/v1/users/new/', data, HTTP_AUTHORIZATION='un token')
        assert response.status_code == 201
        assert response.json()['email'] == response.json()['username']
        assert response.json()['email'] == data['email']

    def test_error_si_no_se_envia_token(self):
        c = Client()
        data = {'email': 'Juancito@gmail.com'}
        response = c.post('/api/v1/users/new/', data)
        assert response.status_code == 400
        assert response.json() == 'error, expected token'

    @patch('users.auth.magiclink.MagicLinkAuth')
    def test_error_si_token_no_es_valido(self, mock):
        _mock = MagicMock()
        reason_invalid = 'token es invalido'
        _mock.didtoken_is_valid = MagicMock(return_value = (False, reason_invalid))
        mock.return_value = _mock
        c = Client()
        data = {'email': 'Juancito@gmail.com'}
        response = c.post('/api/v1/users/new/', data, HTTP_AUTHORIZATION='un token')
        assert response.status_code == 400
        assert response.json() == reason_invalid

    @patch('users.auth.magiclink.MagicLinkAuth')
    def test_error_si_ya_existe_el_usuario(self, mock):
        _mock = MagicMock()
        _mock.didtoken_is_valid = MagicMock(return_value = (True, ''))
        mock.return_value = _mock
        c = Client()
        data = {'email': 'Juancito@gmail.com'}
        self.crear_usuario(data)
        response = c.post('/api/v1/users/new/', data, HTTP_AUTHORIZATION='un token')
        assert response.status_code == 400
        assert response.json() == 'error creating user'

    def crear_usuario(self, data):
        User.objects.create(username=data['email'], **data)


    def test_usuario_existe_por_mail(self):
        c = Client()
        data = {'email': 'Juancito@gmail.com'}
        self.crear_usuario(data)
        email = 'Juancito@gmail.com'
        response = c.get('/api/v1/users/{}'.format(email))
        assert response.status_code == 200

    def test_usuario_no_existe_por_mail(self):
        c = Client()
        email = 'Juancito@gmail.com'
        response = c.get('/api/v1/users/{}'.format(email))
        assert response.status_code == 404
