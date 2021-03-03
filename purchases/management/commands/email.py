from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage

# From django
from django.core.management.base import BaseCommand, CommandError

# From w
from purchases.models import Payment
from purchases.constants import PURCHASE_STATUS_COMPLETED,  \
    PAYMENT_STATUS_RESERVED    
from purchases.signals import capture_payment 


class Command(BaseCommand):
    help = 'Captures the payments of completed purchases'

    def handle(self, *args, **options):
        self.sendmail()
    
    def sendmail(request):
        ctx = {
            'client_firstname': 'diego',
            'client_lastname': '',
            'status': 'DESPACHADO',
            'address': 'Envio: Goya 681 PB, Buenos Aires',
            'link': 'https://google.com.ar',
            'coupon': 'Cupon 30% de descuento',
            'coupon_code': 'PRIMCSZ'
        }
        message = get_template('email_new_coupon.template.html').render(ctx)
        msg = EmailMessage(
            'Subject',
            message,
            'diegobtvtb@gmail.com',
            ['diegobuceta35@gmail.com'],
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

        print("Mail successfully sent")