# From django
from django.conf import settings

import json

# From requests
import requests 
from requests.exceptions import Timeout
from requests.exceptions import ConnectionError

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
            error_msg = 'error timeout'
        except ConnectionError as err:
            error_msg = '{}'.format(err)
        if response.status_code != 201:
            error_msg = '{} [{}]'.format(response.json().get('message',''), \
                    response.json().get('error',''))
        if error_msg:
            return error_msg, False

        return response.json(), True
    
    @classmethod
    def capture(cls, purch_id):
        error_msg = ''
        breakpoint()
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
            error_msg = 'error timeout'
        except ConnectionError as err:
            error_msg = '{}'.format(err)
        
        if response.status_code not in [200, 201]:
            error_msg = '{}'.format(response.json().get('message', ''))
        
        if error_msg:
            return error_msg, False
        
        return response.json(), True
