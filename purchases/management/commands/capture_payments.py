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

        payments_reserved_in_completed_purchase = Payment.objects.filter(
            status=PAYMENT_STATUS_RESERVED,
            individual_purchase__purchase__status=PURCHASE_STATUS_COMPLETED
        )
        
        total_to_update = payments_reserved_in_completed_purchase.count()
        total_updated = 0

        for payment_reserved in payments_reserved_in_completed_purchase:
            res, ok = capture_payment(payment_reserved)
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