# From django
from django.conf import settings

import json

# From requests
import requests 
from requests.exceptions import Timeout
from requests.exceptions import ConnectionError

FAILED_STATUS = 'rejected'
RESERVED_STATUS = 'authorized'
CAPTURED_STATUS = 'captured'

class MercadoPagoPaymentService:
    headers = { 'Authorization': 'Bearer {}'
                .format(settings.MERCADO_PAGO_ACCESS_TOKEN)
    }
    @classmethod
    def do(cls, data):
        error_msg = ''
        data['payer'] = {
            'email': data['payer_email']
        }
        data.pop('payer_email')
        data['capture'] = False
        data['binary_mode'] = True
        try:
            response = requests.post(settings.MERCADO_PAGO_BASE_URL, \
                    json=data, \
                    headers=cls.headers, \
                    timeout=settings.MERCADO_PAGO_TIMEOUT)
        except Timeout:
            return 'error timeout', False
        except ConnectionError as err:
            return '{}'.format(err), False
        
        return cls.parse_response(response=response, expected_status=RESERVED_STATUS)
        
    @classmethod
    def capture(cls, purch_id):
        data = {
            'capture': True
        }

        url = '{}{}'.format(settings.MERCADO_PAGO_BASE_URL, purch_id)
        
        try:
            response = requests.put(url, \
                    json=data, \
                    headers=cls.headers, \
                    timeout=settings.MERCADO_PAGO_TIMEOUT)
        except Timeout:
            return 'error timeout', False
        except ConnectionError as err:
            return '{}'.format(err), False
        
        return cls.parse_response(response=response, expected_status=CAPTURED_STATUS)


    @classmethod
    def parse_response(cls, response, expected_status):
        if response.status_code != 201: 
            error_msg = '{}'.format(response.json().get('message', ''))
            return error_msg, False
        else:
            if response.json()['status'] == expected_status:
                return expected_status, True
            error_msg = '{} {}'.format(response.json()['status'], response.json()['status_detail'])
            return error_msg, False
                
