# From django
from django.core.management.base import BaseCommand, CommandError

# From w
from purchases.models import Payment
from purchases.constants import PURCHASE_STATUS_CANCELLED,  \
    PAYMENT_STATUS_RESERVED    
from purchases.signals import cancel_payment 


class Command(BaseCommand):
    help = 'Returns the payments of cancelled Purchases'

    def handle(self, *args, **options):

        payments_reserved_in_cancelled_purchases = Payment.objects.filter(
            status=PAYMENT_STATUS_RESERVED,
            individual_purchase__purchase__status=PURCHASE_STATUS_CANCELLED
        )
        
        total_to_update = payments_reserved_in_cancelled_purchases.count()
        total_updated = 0

        for payment_reserved in payments_reserved_in_cancelled_purchases:
            res, ok = cancel_payment(payment_reserved)
            if ok:
                total_updated += 1
            else:
                self.stdout.write(self.style.ERROR(
                    '{} {} {}'.format(res, ok,  payment_reserved.id)
                ))
        
        self.stdout.write(self.style.SUCCESS(
            'Resumen de corrida. Total para actualizar: {}, total actualizados: {}'.format(
                total_to_update, total_updated
            )
        ))