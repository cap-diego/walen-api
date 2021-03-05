# From django
from django.core.management.base import BaseCommand, CommandError

# From w
from purchases.models import Payment
from purchases.constants import PURCHASE_STATUS_COMPLETED,  \
    PAYMENT_STATUS_RESERVED    
from purchases.signals import cancel_payment 
from ecommerceapp.time import APIClock

class Command(BaseCommand):
    help = 'Returns the payments of expired and non completed Purchases'

    def handle(self, *args, **options):
        now = APIClock.now()
        payments_reserved_purchase_non_cancelled = Payment.objects.exclude(
            individual_purchase__purchase__status=PURCHASE_STATUS_COMPLETED
        ).filter(
            status=PAYMENT_STATUS_RESERVED
        )
        
        total_to_update = 0
        total_updated = 0

        for payment_reserved in payments_reserved_purchase_non_cancelled:
            
            purchase = payment_reserved.individual_purchase.purchase
            if APIClock.date_is_expired(purchase.expiration_date):
                continue

            total_to_update +=1
            res, ok = cancel_payment(payment_reserved)

            if ok:
                total_updated += 1
            else:
                self.stdout.write(self.style.ERROR(
                    '{} {} {}'.format(res, ok,  payment_reserved.id)
                ))
        
        self.stdout.write(self.style.SUCCESS(
            'Resumen de corrida. Total para cancelar: {}, total cancelados: {}'.format(
                total_to_update, total_updated
            )
        ))
        return